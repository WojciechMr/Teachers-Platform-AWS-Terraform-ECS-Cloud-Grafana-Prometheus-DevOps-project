# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure static files directory exists
RUN mkdir -p /app/staticfiles

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Collect static files (optional if using STATIC_ROOT)
RUN python manage.py collectstatic --noinput

# Start Gunicorn
CMD ["gunicorn", "web.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

