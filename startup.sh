#!/usr/bin/env bash
# Azure App Service startup command:  bash startup.sh
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
# One-time owner account: set DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD as
# app settings, restart once, then delete the PASSWORD setting.
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py createsuperuser --noinput 2>/dev/null || echo "Owner account already exists."
fi
exec gunicorn config.wsgi --bind=0.0.0.0:${PORT:-8000} --workers=2 --threads=4 --timeout=120 --access-logfile=-
