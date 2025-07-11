# ⏰ celery.py - Celery app configuration for Django project

import os

from celery import Celery

# 🌱 Set default Django settings for Celery workers
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

# 🚀 Initialize Celery app
celery_app = Celery("app")

# ⚙️ Load Celery config from Django settings with CELERY_ namespace
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# 🔍 Auto-discover tasks across all installed apps
celery_app.autodiscover_tasks()
