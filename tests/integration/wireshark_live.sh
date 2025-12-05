#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Starting Wireshark Live Capture ===${NC}"
echo ""

# Find Wireshark executable
WIRESHARK_BIN=""
if command -v wireshark &> /dev/null; then
    WIRESHARK_BIN="wireshark"
elif [ -x "/Applications/Wireshark.app/Contents/MacOS/Wireshark" ]; then
    WIRESHARK_BIN="/Applications/Wireshark.app/Contents/MacOS/Wireshark"
else
    echo -e "${YELLOW}Wireshark not found. Please install Wireshark first.${NC}"
    echo "Download from: https://www.wireshark.org/download.html"
    exit 1
fi

# Check if controller container is running
if ! docker ps | grep -q minisdn-controller; then
    echo -e "${YELLOW}Controller container is not running.${NC}"
    echo "Please run 'make manual' or 'make manual-capture' first."
    exit 1
fi

echo -e "${YELLOW}Starting live packet capture...${NC}"
echo -e "${BLUE}This will stream OpenFlow packets (port 6634) to Wireshark in real-time.${NC}"
echo -e "${BLUE}Press Ctrl+C in this terminal to stop the capture.${NC}"
echo ""
echo -e "${GREEN}Wireshark should open in a moment...${NC}"
echo ""

# Stream packets from container to Wireshark
# Using SSH-like pipe: docker exec tcpdump -> wireshark
# -i any: capture on all interfaces
# -U: packet-buffered output (for real-time streaming)
# -w -: write to stdout
# -k: start capturing immediately
# -i -: read from stdin
docker exec minisdn-controller tcpdump -i any -U -w - port 6634 2>/dev/null | "${WIRESHARK_BIN}" -k -i -
