FROM python:3.12-slim

# Install tcpdump for packet capture and curl for uv installation
RUN apt-get update && \
    apt-get install -y tcpdump curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml /app/
COPY uv.lock /app/

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY src/ /app/src/

# Run the controller
CMD ["uv", "run", "python", "-m", "src.main"]
