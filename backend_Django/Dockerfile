# ==============================
# 1. Użyj lekkiego obrazu Pythona
# ==============================
FROM python:3.12-slim

# ==============================
# 2. Ustaw zmienne środowiskowe
# ==============================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==============================
# 3. Ustaw katalog roboczy
# ==============================
WORKDIR /app

# ==============================
# 4. Skopiuj pliki
# ==============================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Upewnij się, że python-dotenv i gunicorn są zainstalowane
RUN pip install --no-cache-dir python-dotenv gunicorn

# ==============================
# 5. Skopiuj cały kod projektu
# ==============================
COPY . .

# ==============================
# 6. Zbierz statyczne pliki
# ==============================
RUN python manage.py collectstatic --noinput || echo "Brak statycznych plików — pomijam"

# ==============================
# 7. Otwórz port 8000
# ==============================
EXPOSE 8000

# ==============================
# 8. Uruchom Gunicorn
# ==============================
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "web.wsgi:application"]
