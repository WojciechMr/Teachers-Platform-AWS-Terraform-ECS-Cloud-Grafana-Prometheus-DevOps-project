import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'edu_db'),
        'USER': os.getenv('DB_USER', 'edu_admin'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'maniekirlandia1'),
        'HOST': os.getenv('DB_HOST', 'edu-db-public.cbuk8souypno.eu-central-1.rds.amazonaws.com'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
