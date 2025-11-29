FROM python:3.12-slim

# Install tcpdump for packet capture
RUN apt-get update && \
    apt-get install -y tcpdump && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source code
COPY src/ /app/src/

# Run the controller
CMD ["python", "-m", "src.main"]
