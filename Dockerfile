FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Rust toolchain
RUN apt-get update && \
    apt-get install -y curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    export CARGO_HOME=$HOME/.cargo && \
    export PATH="$CARGO_HOME/bin:$PATH"

# Set environment variables for writable directories
ENV CARGO_HOME=/app/.cargo
ENV CARGO_TARGET_DIR=/app/target

# Create necessary directories
RUN mkdir -p /app/.cargo /app/target

# Set the working directory to the score directory
WORKDIR /app/score

# Ensure directories are writable
RUN chmod -R 777 /app/.cargo /app/target

# Install dependencies if required
# RUN pip install -r requirements.txt

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
