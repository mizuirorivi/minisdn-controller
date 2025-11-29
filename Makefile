.PHONY: test test-unit test-integration test-packets help clean

help:
	@echo "Available targets:"
	@echo "  make test             - Run all tests (unit + integration)"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests (Docker required)"
	@echo "  make test-packets     - Run packet capture tests (Docker required)"
	@echo "  make test-manual      - Start containers and verify handshake (containers stay running)"
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

clean:
	@echo "Cleaning up..."
	@cd tests/integration && docker-compose down -v 2>/dev/null || true
	@rm -f tests/integration/capture.pcap
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete"
