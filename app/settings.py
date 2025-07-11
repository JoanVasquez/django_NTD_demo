# settings.py - Minimal Django 5, PostgreSQL, Celery (Redis) configuration

import os
from pathlib import Path

from dotenv import load_dotenv

# 🌱 Load environment variables from .env
load_dotenv()

# 🛤️ Base paths
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Security
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")
DEBUG = os.getenv("DEBUG", "False").lower() in {"1", "true", "yes"}
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,web,logstash,elasticsearch,kibana",
).split(",")

# 🚀 Installed apps
INSTALLED_APPS = [
    "rest_framework",
    "django_prometheus",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
    "django_celery_beat",
    "planets",
    "analytics",
]

# 🧩 Middleware
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

# 🪐 Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 🌍 URL & WSGI
ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"

# ⚡ Environment
ENV = os.getenv("ENV", "dev").lower()

# 🗄️ Database configuration
if ENV == "test":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
            "ATOMIC_REQUESTS": False,
            "AUTOCOMMIT": True,
            "CONN_MAX_AGE": 0,
            "OPTIONS": {},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.getenv("POSTGRES_HOST", "postgres"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "NAME": os.getenv("POSTGRES_DB", "demo"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        }
    }

# 🧩 Cache configuration
if ENV == "test":
    # In-memory local cache during tests
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-test-cache",
            "TIMEOUT": None,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL", "redis://redis:6379/0"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

# 📈 Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "logstash": {
            "level": "INFO",
            "class": "logstash.TCPLogstashHandler",
            "host": "logstash",
            "port": 5000,
            "version": 1,
            "message_type": "django",
            "fqdn": False,
            "tags": ["django"],
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "logstash"],
            "level": "INFO",
        },
    },
}

# 🔑 Password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {"NAME": ("django.contrib.auth.password_validation." "MinimumLengthValidator")},
    {"NAME": ("django.contrib.auth.password_validation." "CommonPasswordValidator")},
    {"NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator")},
]

# 🚦 Slash behavior
APPEND_SLASH = False

# ⚙️ REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PARSER_CLASSES": ("rest_framework.parsers.JSONParser",),
    "DEFAULT_SCHEMA_CLASS": ("drf_spectacular.openapi.AutoSchema"),
}

# 📚 API Schema settings
SPECTACULAR_SETTINGS = {
    "TITLE": "My Planets API",
    "DESCRIPTION": ("CRUD operations for Star Wars planets " "via a service layer"),
    "VERSION": "1.0.0",
}

# 🖼️ Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ⏰ Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
CELERY_TIMEZONE = "UTC"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_BEAT_SCHEDULE = {}

# 🗂️ Default primary key type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
