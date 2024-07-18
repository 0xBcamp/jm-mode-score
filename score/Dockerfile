FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Rust toolchain
RUN apt-get update && \
    apt-get install -y curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    source $HOME/.cargo/env

# Set environment variables for writable directories
ENV CARGO_HOME=/app/.cargo
ENV CARGO_TARGET_DIR=/app/target

# Copy application code
COPY ./app /app

# Ensure directories exist and are writable
RUN mkdir -p /app/.cargo /app/target && chmod -R 777 /app/.cargo /app/target

WORKDIR /app
