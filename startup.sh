#!/usr/bin/env bash
# Azure App Service startup command:  bash startup.sh
set -e
# SQLite lives on the persistent /home share (DATABASE_URL=sqlite:////home/data/db.sqlite3).
mkdir -p /home/data 2>/dev/null || true
# Snapshot the database before migrations touch it (no-op without SQLite + Azure Storage).
python manage.py backup_db || echo "Pre-start backup failed; continuing."
python manage.py migrate --noinput
python manage.py collectstatic --noinput
# One-time owner account: set DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD as
# app settings, restart once, then delete the PASSWORD setting.
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py createsuperuser --noinput 2>/dev/null || echo "Owner account already exists."
fi
exec gunicorn config.wsgi --bind=0.0.0.0:${PORT:-8000} --workers=2 --threads=4 --timeout=120 --access-logfile=-
