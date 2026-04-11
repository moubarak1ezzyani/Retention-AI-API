# --- Stage 1: Build Stage ---
# We can use a larger image to build dependencies if needed, 
# but for this project, the slim image is sufficient.
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into a local directory
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt

# --- Stage 2: Final Runtime Stage ---
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Install runtime dependencies (libpq-dev is needed for psycopg2 at runtime if not self-contained)
# Also install curl for the healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Copy installed python packages from the builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy the application code and models
# Ensure ownership is set to the non-root user
COPY --chown=appuser:appuser ./app /app/app
COPY --chown=appuser:appuser ./models /app/models

# Expose the API port
EXPOSE 8000

# Healthcheck to ensure the container is running correctly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]