# --- Bazowy obraz ---
FROM python:3.12-slim

# --- Ustaw katalog roboczy ---
WORKDIR /app

# --- Zmienne środowiskowe ---
ENV PYTHONUNBUFFERED=1

# --- Systemowe zależności dla PostgreSQL i WeasyPrint ---
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info \
    wget \
    fonts-dejavu-core \
    fonts-liberation \
&& rm -rf /var/lib/apt/lists/*

# --- Skopiuj plik requirements i zainstaluj zależności ---
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Skopiuj resztę kodu aplikacji ---
COPY . .

# --- Collect static files ---
RUN python manage.py collectstatic --noinput

# --- Gunicorn nasłuchuje na 0.0.0.0:8000 ---
CMD ["gunicorn", "web.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30", "--access-logfile", "-", "--error-logfile", "-"]

