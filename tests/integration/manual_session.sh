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

echo -e "${YELLOW}=== Manual Integration Session (containers will remain running) ===${NC}"

# Start containers (reuse if already running)
echo -e "${YELLOW}Starting Docker containers...${NC}"
docker-compose up -d

# Wait for controller to be ready
echo -e "${YELLOW}Waiting for controller to start...${NC}"
sleep 3

# Configure OVS
echo -e "${YELLOW}Configuring Open vSwitch...${NC}"
docker exec minisdn-ovs /usr/share/openvswitch/scripts/ovs-ctl start 2>/dev/null || true
sleep 2
docker exec minisdn-ovs ovs-vsctl --if-exists del-br br0
docker exec minisdn-ovs ovs-vsctl add-br br0
docker exec minisdn-ovs ovs-vsctl set-controller br0 tcp:controller:6634
docker exec minisdn-ovs ovs-vsctl set bridge br0 protocols=OpenFlow10
docker exec minisdn-ovs ip link set dev br0 up
sleep 2

# Trigger handshake
echo -e "${YELLOW}Triggering OpenFlow connection...${NC}"
CONTROLLER_IP=$(docker inspect minisdn-controller --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
docker exec minisdn-ovs timeout 5 ovs-ofctl show tcp:$CONTROLLER_IP:6634 >/dev/null 2>&1 || true
sleep 3

# Check logs for handshake
echo -e "${YELLOW}Checking controller logs for handshake...${NC}"
LOGS=$(docker logs minisdn-controller 2>&1 | tail -n 200)

if echo "$LOGS" | grep -q "Hello message received"; then
    echo -e "${GREEN}✓ Hello message observed in controller logs${NC}"
else
    echo -e "${RED}✗ Hello message NOT observed in controller logs${NC}"
fi

if echo "$LOGS" | grep -q "Connection from"; then
    echo -e "${GREEN}✓ OpenFlow connection established${NC}"
else
    echo -e "${RED}✗ OpenFlow connection NOT found in logs${NC}"
fi

echo -e "\n${YELLOW}Containers are still running for inspection.${NC}"
echo -e "${YELLOW}- View logs: docker logs -f minisdn-controller${NC}"
echo -e "${YELLOW}- Inspect OVS: docker exec -it minisdn-ovs bash${NC}"
echo -e "${YELLOW}- Stop and clean up when finished: (from tests/integration) docker-compose down -v${NC}"
