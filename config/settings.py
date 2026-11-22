"""
Django settings for CivicPulse.

Everything that changes between your laptop and AWS is read from environment
variables (or a .env file), so the same code runs in both places.
"""
import os
from pathlib import Path

import dj_database_url
from django.contrib.messages import constants as message_constants
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    return [item.strip() for item in os.environ.get(name, default).split(",") if item.strip()]


# --------------------------------------------------------------------------
# Core
# --------------------------------------------------------------------------
DEBUG = env_bool("DEBUG", False)

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "local-demo-key-change-before-deployment"
    else:
        raise RuntimeError(
            "SECRET_KEY is not set. Copy .env.example to .env and set SECRET_KEY "
            "(see README: python -c \"from django.core.management.utils import "
            "get_random_secret_key as g; print(g())\")."
        )

# Comma separated. Put your EC2 public IP / Elastic IP / domain here.
# Example: ALLOWED_HOSTS=54.164.149.60,ec2-54-164-149-60.compute-1.amazonaws.com
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")

# Needed only when the site is served from a domain/IP with a scheme that differs
# from what the proxy reports, e.g. CSRF_TRUSTED_ORIGINS=http://54.164.149.60
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# --------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "complaints",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "complaints.context_processors.civic_constants",
            ],
        },
    },
]

# --------------------------------------------------------------------------
# Database  (SQLite by default; set DATABASE_URL for PostgreSQL/MySQL on RDS)
#   postgres://user:password@your-db.xxxx.us-east-1.rds.amazonaws.com:5432/civicpulse
# --------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'instance' / 'civicpulse.sqlite3'}",
        conn_max_age=60,
    )
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------
AUTH_USER_MODEL = "complaints.User"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "index"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# Internationalisation
# --------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static files (served by WhiteNoise, so nginx only has to proxy) and uploads
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Uploaded complaint photos live outside STATIC_ROOT and are *not* served
# publicly: they go through a login-protected view (complaints.views.uploaded_file).
MEDIA_ROOT = Path(os.environ.get("UPLOAD_FOLDER", BASE_DIR / "uploads"))
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_PERMISSIONS = 0o640

# Bootstrap uses "danger", Django uses "error".
MESSAGE_TAGS = {message_constants.ERROR: "danger"}

# --------------------------------------------------------------------------
# Security
#
# IMPORTANT for AWS: leave USE_HTTPS=0 until you have installed a certificate.
# Turning it on without HTTPS makes the browser redirect to https:// (port 443),
# which is closed by default -> "This site can't be reached / timed out".
# --------------------------------------------------------------------------
USE_HTTPS = env_bool("USE_HTTPS", False)

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

if USE_HTTPS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", 3600))

# --------------------------------------------------------------------------
# Logging (goes to stdout -> journald / CloudWatch agent)
# --------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
}
