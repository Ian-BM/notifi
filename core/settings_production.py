"""
Production settings — imported on the server, never commit secrets.

Activated via DJANGO_SETTINGS_MODULE=core.settings_production
(set in deploy/notifi.service and deploy/.env.production).
"""
from .settings import *  # noqa: F401,F403
import os

# Security
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
ALLOWED_HOSTS = [
    host for host in [
        'notifi.co.tz',
        'www.notifi.co.tz',
        os.environ.get('SERVER_IP', ''),
    ] if host
]

# Database — PostgreSQL on server. Always PostgreSQL in production,
# regardless of any DB_ENGINE override used for local development.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'notifi_db'),
        'USER': os.environ.get('DB_USER', 'notifi_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files: WhiteNoise middleware + CompressedManifestStaticFilesStorage
# are already configured in core/settings.py — nothing to add here.

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
# Gunicorn only ever speaks plain HTTP — Nginx terminates TLS in front of
# it. Without this, Django can't tell a real HTTPS request (proxied with
# X-Forwarded-Proto: https) from a plain one, and SECURE_SSL_REDIRECT
# above causes an infinite redirect loop on every request. Safe because
# gunicorn binds to 127.0.0.1 only — Nginx is the sole caller.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/notifi/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Beem API
BEEM_API_KEY = os.environ.get('BEEM_API_KEY', BEEM_API_KEY)
BEEM_SECRET_KEY = os.environ.get('BEEM_SECRET_KEY', BEEM_SECRET_KEY)

# Support contacts (shown in platform UI)
SUPPORT_PHONE = os.environ.get('SUPPORT_PHONE', SUPPORT_PHONE)
SUPPORT_WHATSAPP = os.environ.get('SUPPORT_WHATSAPP', SUPPORT_WHATSAPP)
