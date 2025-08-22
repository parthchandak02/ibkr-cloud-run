# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for SSL certificates
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install uv for faster package management
RUN pip install uv

# Install Python dependencies using uv (much faster!)
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application code
COPY main.py .

# Create directory for OAuth files (will be populated from secrets)
RUN mkdir -p /app/oauth_files

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
