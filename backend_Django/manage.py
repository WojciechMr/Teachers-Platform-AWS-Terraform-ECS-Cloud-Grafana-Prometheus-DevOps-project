#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv

# Wczytanie lokalnego pliku .env (tylko dla lokalnych testów)
load_dotenv()

if __name__ == "__main__":
    # Domyślny settings module -> prod (zgodnie z infrastrukturą)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings.prod")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
