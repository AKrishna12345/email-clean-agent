FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will use PORT env var)
EXPOSE 8080

# Run the application
# Railway provides PORT environment variable automatically
# Use shell form to allow environment variable expansion
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]

