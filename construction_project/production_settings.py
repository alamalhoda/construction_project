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

# تنظیمات زمان برای production
TIME_ZONE = 'Asia/Tehran'
USE_TZ = True
USE_I18N = True
USE_L10N = True

# تنظیمات Cache برای Render (Local Memory)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# تنظیمات Logging برای Production
# استفاده از logging کامل از settings.py با تنظیمات مناسب برای production
# فقط سطح لاگ را برای production تنظیم می‌کنیم (INFO به جای DEBUG)
from pathlib import Path

# تعیین سطح لاگ برای production
DASHBOARD_LOG_LEVEL = 'INFO'
API_LOG_LEVEL = 'INFO'
CALCULATIONS_LOG_LEVEL = 'WARNING'
DJANGO_LOG_LEVEL = 'WARNING'

# اطمینان از وجود پوشه logs
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# تنظیمات Logging کامل برای Production (مشابه settings.py اما با سطح INFO)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # Dashboard Logging - RotatingFileHandler (بر اساس اندازه)
        'dashboard_file': {
            'level': DASHBOARD_LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'dashboard.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # API Logging - RotatingFileHandler (بر اساس اندازه)
        'api_file': {
            'level': API_LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'api.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # Calculations Logging - TimedRotatingFileHandler (بر اساس زمان)
        'calculations_file': {
            'level': CALCULATIONS_LOG_LEVEL,
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOGS_DIR / 'calculations.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,  # نگه داشتن 30 روز
            'formatter': 'verbose',
        },
        # Security Logging - TimedRotatingFileHandler (بر اساس زمان)
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,  # نگه داشتن 30 روز
            'formatter': 'verbose',
        },
        # Django General Logging - RotatingFileHandler (بر اساس اندازه)
        'django_file': {
            'level': DJANGO_LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_file'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'django_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'dashboard': {
            'handlers': ['console', 'dashboard_file'],
            'level': DASHBOARD_LOG_LEVEL,
            'propagate': False,
        },
        'dashboard.views': {
            'handlers': ['console', 'dashboard_file'],
            'level': DASHBOARD_LOG_LEVEL,
            'propagate': False,
        },
        'construction.api': {
            'handlers': ['console', 'api_file'],
            'level': API_LOG_LEVEL,
            'propagate': False,
        },
        'construction.calculations': {
            'handlers': ['console', 'calculations_file'],
            'level': CALCULATIONS_LOG_LEVEL,
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
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
