# Base image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure static files directory exists
RUN mkdir -p /app/staticfiles

# Expose port 8000
EXPOSE 8000

# Set environment variables (optional defaults; w ECS Task Definition możesz nadpisać)
ENV DJANGO_DEBUG=False
ENV DJANGO_ALLOWED_HOSTS=edu-app-alb-507939115.eu-central-1.elb.amazonaws.com
ENV DJANGO_SECRET_KEY=q6v$ysg&2sx%&gdn@qz&nlnt83r5wwyql(+wne#&b=fl2=*t3a
ENV DB_NAME=edu_db
ENV DB_USER=edu_admin
ENV DB_PASSWORD=xxxxxx
ENV DB_HOST=edu-db-public.cbuk8souypno.eu-central-1.rds.amazonaws.com
ENV DB_PORT=5432

# Collect static files (opcja, jeśli używasz STATIC_ROOT)
RUN python manage.py collectstatic --noinput

# Start Gunicorn
CMD ["gunicorn", "web.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
