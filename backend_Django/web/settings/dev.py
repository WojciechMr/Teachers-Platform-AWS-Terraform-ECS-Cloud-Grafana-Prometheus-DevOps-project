from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# 🔹 Lokalna baza SQLite do testów dev
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

# 🔹 Statyczne pliki lokalnie
STATICFILES_DIRS = [
    BASE_DIR / "app/static",
]
