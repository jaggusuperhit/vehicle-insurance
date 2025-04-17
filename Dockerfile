# Use an official Python 3.10 image from Docker Hub
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/

# Copy application code first (needed for -e . installation)
COPY . /app

# Install Python dependencies
RUN sed -i 's/-e \.\.\.\./-e ./' requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/artifact/production_model /app/data /app/sample_data

# Copy sample data
COPY data/data.csv /app/data/
COPY sample_data/insurance_data.csv /app/sample_data/

# Expose the port FastAPI will run on
EXPOSE 5050

# Set environment variables with default values
ENV APP_PORT=5050
ENV APP_HOST=0.0.0.0

# Create a startup script
RUN echo '#!/bin/bash\n\
    python -c "from src.utils.model_utils import ensure_production_model_exists; ensure_production_model_exists()"\n\
    python app.py' > /app/start.sh && \
    chmod +x /app/start.sh

# Command to run the startup script
CMD ["/app/start.sh"]