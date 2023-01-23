"""
Django settings for django_lowcoder project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import json
import os
import sys
from pathlib import Path

# noinspection PyPackageRequirements
import environ  # type: ignore
from django.contrib.messages import constants as message_constants
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32))
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "")

DEBUG = os.getenv("DEBUG", False) == "True"
sys.stdout.write(f"DEBUG: {DEBUG}\r")

DATABASE_URL = os.getenv("DATABASE_URL", "")
sys.stdout.write(f"DATABASE_URL from environment: {DATABASE_URL}\r")

VCAP_SERVICES = os.getenv("VCAP_SERVICES", "")
# sys.stdout.write(f"VCAP_SERVICES from environment: {VCAP_SERVICES}\r")

if VCAP_SERVICES:
    sys.stdout.write("VCAP_SERVICES available\r")
    vcap_services_data = json.loads(VCAP_SERVICES)
    credentials = vcap_services_data["osb-postgres"][0]["credentials"]
    uri = vcap_services_data["osb-postgres"][0]["credentials"]["uri"]
    db_url = uri.replace(
        f"targetServerType={credentials['targetServerType']}\u0026\u0026", ""
    )
    db_url = db_url.replace(f"sslfactory={credentials['sslfactory']}", "")
    db_url = db_url.replace(f"sslmode={credentials['sslmode']}", f"sslmode=disable")
    DATABASE_URL = db_url
    sys.stdout.write(f"DATABASE_URL from VCAP_SERVICES: {DATABASE_URL}\r")

if VCAP_SERVICES:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Application definition

INSTALLED_APPS = [
    "rosetta",
    "project.apps.ProjectConfig",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_extensions",
    "django_htmx",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

if DEBUG:
    INSTALLED_APPS.insert(0, "debug_toolbar")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

CORS_ORIGIN_ALLOW_ALL = os.getenv("CORS_ORIGIN_ALLOW_ALL", False) == "True"
CORS_ORIGIN_WHITELIST = os.environ.get(
    "CORS_ORIGIN_WHITELIST", "http://localhost:8000"
).split(",")

ROOT_URLCONF = "django_lowcoder.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "django_lowcoder.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if DATABASE_URL:
    DATABASES = {"default": env.db_url_config(DATABASE_URL)}


# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "de-de"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# The absolute path to the directory where collectstatic
# will collect static files for deployment.
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# URL to use when referring to static files located in STATIC_ROOT.
STATIC_URL = "static/"

# This setting defines the additional locations the staticfiles app
# will traverse if the FileSystemFinder finder is enabled,
# e.g. if you use the collectstatic or findstatic management command
# or use the static file serving view.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),  # needed, because using outside all apps
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_ROOT = "upload/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_FAIL_SILENTLY = not DEBUG

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
}

ROSETTA_SHOW_AT_ADMIN_PANEL = True
ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True

LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
]

MESSAGE_TAGS = {
    message_constants.DEBUG: "debug",
    message_constants.INFO: "info",
    message_constants.SUCCESS: "success",
    message_constants.WARNING: "warning",
    message_constants.ERROR: "danger",
}

if vcap_services_data:
    if "mail-service" in vcap_services_data:
        mail_credentials = vcap_services_data["mail-service"][0]["credentials"]
        smtp_server = mail_credentials["host"]
        smtp_port = mail_credentials["port"]
        smtp_user = mail_credentials["user"]
        smtp_password = mail_credentials["password"]
        EMAIL_HOST = smtp_server
        EMAIL_PORT = smtp_port
        EMAIL_USER = smtp_user
        EMAIL_HOST_PASSWORD = smtp_password
        EMAIL_USE_LOCALTIME = True

    if "p.redis" in vcap_services_data:
        redis_credentials = vcap_services_data["p.redis"][0]["credentials"]
        redis_host = redis_credentials["host"]
        redis_port = redis_credentials["port"]
        if "user" in redis_credentials:
            redis_user = redis_credentials["user"]
        else:
            redis_user = ""
        redis_user = redis_credentials["user"]
        redis_password = redis_credentials["password"]
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': [
                    f'redis://{redis_user}:{redis_password}@{redis_host}:{redis_port}',
                    ],
                }
            }
