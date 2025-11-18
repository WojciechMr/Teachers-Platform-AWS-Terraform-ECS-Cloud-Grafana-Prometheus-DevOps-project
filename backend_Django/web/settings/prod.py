# backend_Django/web/settings/prod.py
from .base import *
import os

# --- Tryb produkcyjny ---
DEBUG = False

# --- Bezpieczeństwo ---
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# --- Hosty (z .env) ---
env_hosts = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in env_hosts.split(",") if h.strip()]

# --- Proxy / HTTPS nagłówki ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- CSRF / CORS (jeśli masz frontend na HTTPS) ---
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://edublinkier.com",
    "https://www.edublinkier.com",
]
CSRF_TRUSTED_ORIGINS = [
    "https://edublinkier.com",
    "https://www.edublinkier.com",
]

# --- Logging ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# --- Statyczne pliki ---
#STATIC_ROOT = os.path.join(BASE_DIR, "static")
#STATIC_URL = "/static/"

# --- Dla bezpieczeństwa health checków ---
# ALB nie ustawia Host header poprawnie, więc /health/ jest dozwolone bez walidacji
# (reszta ruchu przechodzi normalnie przez ALLOWED_HOSTS)
INSTALLED_APPS += ["storages"]

AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
AWS_S3_REGION_NAME = "eu-central-1"
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False

STATIC_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/static/"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"