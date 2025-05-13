# Use the specified Python Alpine base image
FROM python:3.12.10-alpine3.21

# Add OpenContainers labels
LABEL org.opencontainers.image.source="https://github.com/zchryr/health"

# Set working directory
WORKDIR /app

# Update and upgrade all packages, then clean up
RUN apk update && \
    apk upgrade && \
    apk add --no-cache gcc musl-dev && \
    rm -rf /var/cache/apk/*

# Create a non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    # Remove pip cache
    rm -rf /root/.cache/pip/*

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Disable Python from writing .pyc files
    PYTHONFAULTHANDLER=1 \
    # Enable better error messages
    PYTHONHASHSEED=random \
    # Randomize Python hash seed
    PIP_NO_CACHE_DIR=off \
    # Disable pip cache
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # Disable pip version check
    PIP_DEFAULT_TIMEOUT=100

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]