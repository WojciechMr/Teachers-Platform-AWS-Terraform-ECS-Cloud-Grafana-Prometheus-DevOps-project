# Pobieramy oficjalny obraz Pythona
FROM python:3.12-slim

# Ustawiamy katalog roboczy w kontenerze
WORKDIR /app

# Kopiujemy pliki zależności
COPY requirements.txt .

# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę aplikacji
COPY . .

# Exponujemy port Django
EXPOSE 8000

# Komenda startowa (uruchamia dev server Django)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Zainstaluj klienta PostgreSQL
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
