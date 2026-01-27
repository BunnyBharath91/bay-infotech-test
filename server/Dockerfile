# Multi-stage build for AI Help Desk backend

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first for better performance
RUN pip install --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install CPU-only torch first (much faster than full torch, ~5x smaller)
# This significantly reduces build time
RUN pip install --no-cache-dir --user torch --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies (torch is already installed, so it won't reinstall)
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts are executable
RUN chmod +x scripts/*.py

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
# Use PORT environment variable (Railway sets this automatically)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
