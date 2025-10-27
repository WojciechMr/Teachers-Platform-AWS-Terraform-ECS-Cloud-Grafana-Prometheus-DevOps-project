# --- Bazowy obraz ---
FROM python:3.12-slim

# --- Ustaw katalog roboczy ---
WORKDIR /app

# --- Zmienne środowiskowe ---
ENV PYTHONUNBUFFERED=1

# --- Systemowe zależności dla PostgreSQL ---
RUN apt-get update && apt-get install -y build-essential libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# --- Skopiuj plik requirements i zainstaluj zależności ---
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --- Skopiuj resztę kodu aplikacji ---
COPY . .

# --- Collect static files ---
# Jeśli w .env masz ustawione zmienne środowiskowe, Dockerfile je użyje automatycznie
RUN python manage.py collectstatic --noinput

# --- Gunicorn nasłuchuje na 0.0.0.0:8000 ---
CMD ["gunicorn", "web.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30", "--access-logfile", "-", "--error-logfile", "-"]
