FROM python:3.11-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/config && \
    chmod 755 /app/config

# Install requirements first for better caching
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PORT=5000
EXPOSE 5000

CMD ["python", "app.py"] 