#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Container/constants for packet capture
CAPTURE_CONTAINER="minisdn-controller"
CAPTURE_PATH="/tmp/capture.pcap"
TCPDUMP_PID_FILE="/tmp/tcpdump.pid"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== OpenFlow Packet Capture Test ===${NC}"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    # Stop tcpdump if still running (pid file is inside the container)
    docker exec "$CAPTURE_CONTAINER" sh -c "if [ -f \"$TCPDUMP_PID_FILE\" ]; then kill \$(cat \"$TCPDUMP_PID_FILE\") 2>/dev/null || true; fi" 2>/dev/null || true
    # Copy capture file before cleanup
    docker cp "$CAPTURE_CONTAINER":"$CAPTURE_PATH" "${SCRIPT_DIR}/capture.pcap" 2>/dev/null || true
    docker-compose down -v 2>/dev/null || true
}

# Set trap to ensure cleanup on exit
trap cleanup EXIT INT TERM

# Clean up any existing containers
echo -e "${YELLOW}Cleaning up existing containers...${NC}"
docker-compose down -v 2>/dev/null || true

# Start containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
docker-compose up -d

# Wait for controller to be ready
echo -e "${YELLOW}Waiting for controller to start...${NC}"
sleep 3

# Start tcpdump in background on controller container
echo -e "${YELLOW}Starting packet capture (tcpdump)...${NC}"
docker exec "$CAPTURE_CONTAINER" sh -c "command -v tcpdump >/dev/null 2>&1 || { echo 'tcpdump not found in capture container' >&2; exit 1; }; tcpdump -i any -U -w \"$CAPTURE_PATH\" port 6634 >/tmp/tcpdump.log 2>&1 & echo \$! > \"$TCPDUMP_PID_FILE\""

# Give tcpdump time to start
sleep 2

# Configure OVS and start ovs-vswitchd
echo -e "${YELLOW}Configuring Open vSwitch...${NC}"

# Start ovsdb-server if not running
docker exec minisdn-ovs /usr/share/openvswitch/scripts/ovs-ctl start 2>/dev/null || true

# Wait for OVS to be ready
sleep 2

# Delete bridge if it exists and recreate it (ensures clean state)
docker exec minisdn-ovs ovs-vsctl --if-exists del-br br0
docker exec minisdn-ovs ovs-vsctl add-br br0

# Set controller
docker exec minisdn-ovs ovs-vsctl set-controller br0 tcp:controller:6634

# Bring up the bridge interface
docker exec minisdn-ovs ip link set dev br0 up

# Wait for ovs-vswitchd to pick up the new configuration
sleep 2

# Trigger OpenFlow connection by doing an ovs-ofctl operation directly to the controller
echo -e "${YELLOW}Triggering OpenFlow connection...${NC}"
CONTROLLER_IP=$(docker inspect minisdn-controller --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
docker exec minisdn-ovs ovs-ofctl show tcp:$CONTROLLER_IP:6634 >/dev/null 2>&1 &
OVS_PID=$!

# Wait for handshake to complete
echo -e "${YELLOW}Waiting for OpenFlow handshake...${NC}"
sleep 3

# Kill the ovs-ofctl process
kill $OVS_PID 2>/dev/null || true

# Stop tcpdump
echo -e "${YELLOW}Stopping packet capture...${NC}"
docker exec "$CAPTURE_CONTAINER" sh -c "if [ -f \"$TCPDUMP_PID_FILE\" ]; then kill \$(cat \"$TCPDUMP_PID_FILE\") 2>/dev/null || true; fi" 2>/dev/null || true
sleep 1

# Analyze captured packets
echo -e "${YELLOW}Analyzing captured packets...${NC}"

# Ensure capture file exists before analysis
if ! docker exec "$CAPTURE_CONTAINER" test -f "$CAPTURE_PATH"; then
    echo -e "${RED}✗ Capture file not found at $CAPTURE_PATH in $CAPTURE_CONTAINER${NC}"
    exit 1
fi

# Display packet capture in hex format
echo -e "\n${YELLOW}--- Packet Capture (Hexadecimal) ---${NC}"
docker exec "$CAPTURE_CONTAINER" tcpdump -r "$CAPTURE_PATH" -X 2>/dev/null | head -100

# Check for OpenFlow message types
echo -e "\n${YELLOW}Verifying OpenFlow message types...${NC}"

# Read the pcap file and check for specific byte patterns
PCAP_HEX=$(docker exec "$CAPTURE_CONTAINER" tcpdump -r "$CAPTURE_PATH" -xx 2>/dev/null || true)

if [ -z "$PCAP_HEX" ]; then
    echo -e "${RED}✗ Failed to read capture; tcpdump returned no data${NC}"
    exit 1
fi

# OpenFlow 1.0 version byte: 0x01
# OFPT_HELLO: type=0x00
# OFPT_FEATURES_REQUEST: type=0x05
# OFPT_FEATURES_REPLY: type=0x06

# Check for OFPT_HELLO (version=01, type=00)
if echo "$PCAP_HEX" | grep -q "0x0000:.*01.*00"; then
    echo -e "${GREEN}✓ OFPT_HELLO messages detected${NC}"
else
    echo -e "${RED}✗ OFPT_HELLO messages NOT detected${NC}"
    exit 1
fi

# Check for OFPT_FEATURES_REQUEST or OFPT_FEATURES_REPLY
if echo "$PCAP_HEX" | grep -q "0x0000:.*01.*05\|0x0000:.*01.*06"; then
    echo -e "${GREEN}✓ OFPT_FEATURES_REQUEST/REPLY messages detected${NC}"
else
    echo -e "${RED}✗ OFPT_FEATURES messages NOT detected${NC}"
    exit 1
fi

# Copy capture file to host
echo -e "\n${YELLOW}Saving capture file to ${SCRIPT_DIR}/capture.pcap${NC}"
docker cp "$CAPTURE_CONTAINER":"$CAPTURE_PATH" "${SCRIPT_DIR}/capture.pcap"

echo -e "${GREEN}✓ Capture file saved${NC}"
echo -e "${YELLOW}You can analyze it with: wireshark ${SCRIPT_DIR}/capture.pcap${NC}"

echo -e "\n${GREEN}=== All packet capture tests passed! ===${NC}"
