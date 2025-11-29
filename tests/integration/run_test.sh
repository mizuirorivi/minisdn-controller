#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== OpenFlow Integration Test ===${NC}"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
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

# Check controller logs for handshake messages
echo -e "${YELLOW}Verifying OpenFlow handshake...${NC}"
LOGS=$(docker logs minisdn-controller 2>&1)

if echo "$LOGS" | grep -q "Hello message received"; then
    echo -e "${GREEN}✓ Hello message received${NC}"
else
    echo -e "${RED}✗ Hello message NOT received${NC}"
    echo -e "${YELLOW}Controller logs:${NC}"
    echo "$LOGS"
    exit 1
fi

if echo "$LOGS" | grep -q "Connection from"; then
    echo -e "${GREEN}✓ OpenFlow connection established${NC}"
else
    echo -e "${RED}✗ OpenFlow connection NOT established${NC}"
    echo -e "${YELLOW}Controller logs:${NC}"
    echo "$LOGS"
    exit 1
fi

echo -e "\n${GREEN}=== All tests passed! ===${NC}"
