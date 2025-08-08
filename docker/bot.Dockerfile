# Multi-stage build for production
FROM python:3.11-slim as builder

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user first
RUN adduser --disabled-password --gecos '' appuser

# Copy Python packages from builder to appuser location
COPY --from=builder /root/.local /home/appuser/.local

# Set ownership of packages
RUN chown -R appuser:appuser /home/appuser/.local

# Add user binaries to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY . .
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Run the bot
CMD ["python", "main.py"]