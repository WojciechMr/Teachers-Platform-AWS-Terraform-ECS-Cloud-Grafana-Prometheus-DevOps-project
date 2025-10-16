import os
from pathlib import Path
from dotenv import load_dotenv

# ======================
# Paths
# ======================
BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# Load environment variables from .env
# ======================
load_dotenv(BASE_DIR / '.env')

# ======================
# Django secret key
# ======================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-secret-key')

# ======================
# Debug mode
# ======================
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'

# ======================
# Allowed hosts
# ======================
ALLOWED_HOSTS = ['*']

# ======================
# Database configuration
# ======================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'edu_db'),
        'USER': os.getenv('DB_USER', 'edu_admin'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ======================
# Static & media files (optional)
# ======================
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# ======================
# Other settings...
# ======================
# Możesz tu dodać pozostałe ustawienia Django, np. INSTALLED_APPS, MIDDLEWARE itp.
