#!/usr/bin/env bash
set -e

# ▸ Solo el servicio que establezca RUN_MIGRATIONS=1 ejecutará migrate
if [ "$RUN_MIGRATIONS" = "1" ]; then
  echo "» Making migrations…"
  python manage.py makemigrations --noinput

  echo "» Running Django migrations…"
  python manage.py migrate --noinput
fi

# ——————————————————————————
#  One-off fetch of planets (via Celery)…
# ——————————————————————————
echo "» One-off fetch of planets (via Celery)…"
python manage.py shell -c "from planets.tasks import fetch_and_store_planets; fetch_and_store_planets.apply_async()"

# ▸ Pasa el control al comando real (gunicorn, celery, etc.)
exec "$@"
