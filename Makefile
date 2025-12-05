.PHONY: test test-unit test-integration test-packets test-manual manual manual-capture capture wireshark help clean

help:
	@echo "Available targets:"
	@echo "  make test             - Run all tests (unit + integration)"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests (Docker required)"
	@echo "  make test-packets     - Run packet capture tests (Docker required)"
	@echo "  make test-manual      - Start containers and verify handshake (containers stay running)"
	@echo "  make manual           - Start development environment with auto Wireshark (controller + OVS + Wireshark)"
	@echo "  make manual-capture   - Start development environment with packet capture"
	@echo "  make capture          - Export packet capture to ./openflow_capture.pcap and open in Wireshark"
	@echo "  make wireshark        - Open Wireshark with LIVE packet capture (requires running containers)"
	@echo "  make clean            - Clean up test artifacts"

test: test-unit test-integration

test-unit:
	@echo "Running unit tests..."
	python3 -m unittest discover tests/unit

test-integration:
	@echo "Running integration tests..."
	@cd tests/integration && ./run_test.sh

test-packets:
	@echo "Running packet capture tests..."
	@cd tests/integration && ./verify_packets.sh

test-manual:
	@echo "Running manual integration session (containers will remain running)..."
	@cd tests/integration && ./manual_session.sh

manual:
	@cd tests/integration && ./start_manual.sh

manual-capture:
	@cd tests/integration && ./start_manual_capture.sh

capture:
	@echo "Exporting packet capture from controller container..."
	@docker cp minisdn-controller:/tmp/openflow_capture.pcap ./openflow_capture.pcap 2>/dev/null || { echo "Error: Capture file not found. Did you run 'make manual-capture'?"; exit 1; }
	@echo "Opening in Wireshark..."
	@open -a Wireshark ./openflow_capture.pcap 2>/dev/null || { echo "Capture exported to ./openflow_capture.pcap"; echo "Open it with: wireshark ./openflow_capture.pcap"; }

wireshark:
	@cd tests/integration && ./wireshark_live.sh

clean:
	@echo "Cleaning up..."
	@cd tests/integration && docker-compose down -v 2>/dev/null || true
	@rm -f tests/integration/capture.pcap
	@rm -f openflow_capture.pcap
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete"
