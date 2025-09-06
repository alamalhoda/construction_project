"""
تنظیمات محیط Production
Production Settings for Construction Project
"""

from .settings import *

# تنظیمات امنیتی برای محیط Production
DEBUG = False
ALLOWED_HOSTS = ['*']  # Render will provide the actual domain

# تنظیمات امنیتی SSL (غیرفعال برای Codespaces)
SECURE_SSL_REDIRECT = False  # Codespaces از HTTPS خودکار استفاده می‌کند
SESSION_COOKIE_SECURE = False  # برای development
CSRF_COOKIE_SECURE = False  # برای development
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# تنظیمات دیتابیس برای Codespaces (SQLite - Persistent)
import os

# انتخاب دیتابیس بر اساس environment variable
if os.environ.get('USE_SQLITE', 'true').lower() == 'true':
    # SQLite برای Codespaces (persistent storage)
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'database' / 'online.sqlite3',
        }
    }
else:
    # PostgreSQL برای production
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'construction_db'),
            'USER': os.environ.get('DB_USER', 'construction_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# تنظیمات Static Files برای Render
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# تنظیمات Whitenoise برای static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_MANIFEST_STRICT = False  # برای فایل‌های گمشده سخت‌گیر نباشد

# تنظیمات Cache برای Render (Local Memory)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# تنظیمات Logging برای Render
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# تنظیمات Email برای Render
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # برای تست
# برای production واقعی، تنظیمات SMTP را فعال کنید:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# تنظیمات Session
SESSION_COOKIE_AGE = 3600  # 1 ساعت
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# تنظیمات CSRF
CSRF_COOKIE_AGE = 3600
CSRF_COOKIE_HTTPONLY = True

# تنظیمات Security Headers
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

print("🔒 Production settings loaded - API authentication is REQUIRED")
