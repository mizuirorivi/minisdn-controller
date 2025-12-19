#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Starting Manual Development Environment ===${NC}"
echo ""

# Start containers (source code is mounted as volume for live updates)
echo -e "${YELLOW}[1/4] Starting Docker containers...${NC}"
docker-compose up -d

# Wait for controller to be ready
echo -e "${YELLOW}[2/4] Waiting for controller to start (3 seconds)...${NC}"
sleep 3

# Configure OVS
echo -e "${YELLOW}[3/5] Configuring Open vSwitch...${NC}"
docker exec minisdn-ovs /usr/share/openvswitch/scripts/ovs-ctl start 2>/dev/null || true
sleep 2
docker exec minisdn-ovs ovs-vsctl --if-exists del-br br0
docker exec minisdn-ovs ovs-vsctl add-br br0
docker exec minisdn-ovs ovs-vsctl set bridge br0 protocols=OpenFlow10

# Get controller IP
CONTROLLER_IP=$(docker inspect minisdn-controller --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
echo -e "${YELLOW}Controller IP: ${GREEN}${CONTROLLER_IP}${NC}"

# Start tcpdump BEFORE connecting OVS to controller
echo -e "${YELLOW}[4/5] Starting packet capture (before OpenFlow connection)...${NC}"
# Auto-start Wireshark if available
WIRESHARK_BIN=""
if command -v wireshark &> /dev/null; then
    WIRESHARK_BIN="wireshark"
elif [ -x "/Applications/Wireshark.app/Contents/MacOS/Wireshark" ]; then
    WIRESHARK_BIN="/Applications/Wireshark.app/Contents/MacOS/Wireshark"
fi

if [ -n "$WIRESHARK_BIN" ]; then
    echo -e "  ${GREEN}Starting Wireshark with live packet capture...${NC}"
    # Start Wireshark in background
    (docker exec minisdn-controller tcpdump -i any -U -w - port 6634 2>/dev/null | "${WIRESHARK_BIN}" -k -i - &) >/dev/null 2>&1
    sleep 2
    echo -e "  ${GREEN}✓ Wireshark started${NC}"
else
    echo -e "  ${YELLOW}⚠ Wireshark not found, skipping live capture${NC}"
fi

# Set controller (use IP address instead of hostname for reliability)
echo -e "${YELLOW}[5/5] Connecting OVS to controller and establishing OpenFlow connection...${NC}"
docker exec minisdn-ovs ovs-vsctl set-controller br0 tcp:${CONTROLLER_IP}:6634
docker exec minisdn-ovs ovs-vsctl set bridge br0 fail-mode=standalone
docker exec minisdn-ovs ovs-vsctl set controller br0 max-backoff=1000
docker exec minisdn-ovs ip link set dev br0 up

# Create dummy interfaces to trigger port events (this forces OVS to connect)
# sleep 1
# docker exec minisdn-ovs ip link add veth0 type veth peer name veth1 2>/dev/null || true
# docker exec minisdn-ovs ip link set veth0 up 2>/dev/null || true
# docker exec minisdn-ovs ip link set veth1 up 2>/dev/null || true
# docker exec minisdn-ovs ovs-vsctl add-port br0 veth0 2>/dev/null || true
# sleep 2

# # Send a packet to trigger connection
# docker exec minisdn-ovs ip addr add 10.0.0.1/24 dev veth1 2>/dev/null || true
# docker exec minisdn-ovs ping -c 1 -W 1 10.0.0.2 >/dev/null 2>&1 || true
# sleep 1

echo ""
echo -e "${GREEN}✓ Environment is ready!${NC}"
echo ""

# Show connection status
echo -e "${YELLOW}Connection Status:${NC}"
LOGS=$(docker logs minisdn-controller 2>&1 | tail -n 50)
if echo "$LOGS" | grep -q "Connection from"; then
    echo -e "  ${GREEN}✓ Controller received OpenFlow connection${NC}"
else
    echo -e "  ${YELLOW}⚠ No OpenFlow connection detected yet${NC}"
    echo -e "    Try: docker exec minisdn-ovs ovs-ofctl show tcp:${CONTROLLER_IP}:6634"
fi
echo ""

echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  ${GREEN}View controller logs:${NC}  docker logs -f minisdn-controller"
echo -e "  ${GREEN}Restart Wireshark:${NC}     make wireshark  (if closed)"
echo -e "  ${GREEN}Access OVS shell:${NC}      docker exec -it minisdn-ovs sh"
echo -e "  ${GREEN}Check OVS status:${NC}      docker exec minisdn-ovs ovs-vsctl show"
echo -e "  ${GREEN}Monitor OpenFlow:${NC}      docker exec minisdn-ovs ovs-ofctl dump-flows br0"
echo -e "  ${GREEN}Test connection:${NC}       docker exec minisdn-ovs ovs-ofctl show tcp:${CONTROLLER_IP}:6634"
echo -e "  ${GREEN}Stop environment:${NC}      make clean  (or: cd tests/integration && docker-compose down -v)"
echo ""
