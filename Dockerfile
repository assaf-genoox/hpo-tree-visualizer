# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY hpo_backend.py .
COPY hpo_frontend.html .
COPY hp.json .

# Create a simple nginx config for serving static files
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Copy nginx config
COPY nginx.conf /etc/nginx/sites-available/default

# Expose port
EXPOSE 80

# Start both nginx and the API
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
