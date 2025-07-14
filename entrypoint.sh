#!/usr/bin/env bash
set -e

# Only run migrations when RUN_MIGRATIONS=1 is set
if [ "$RUN_MIGRATIONS" = "1" ]; then
  echo "» Making migrations…"
  python manage.py makemigrations --noinput

  echo "» Applying Django migrations…"
  python manage.py migrate --noinput
fi

# One-time fetch of planets using Celery
echo "» One-off fetch of planets (via Celery)…"
python manage.py shell -c "from planets.tasks import fetch_and_store_planets; fetch_and_store_planets.apply_async()"

# Hand off to the main command (e.g., gunicorn, celery worker, etc.)
exec "$@"
