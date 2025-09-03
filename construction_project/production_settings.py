"""
تنظیمات محیط Production
Production Settings for Construction Project
"""

from .settings import *

# تنظیمات امنیتی برای محیط Production
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']  # دامنه واقعی خود را وارد کنید

# تنظیمات امنیتی SSL
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# تنظیمات دیتابیس Production (PostgreSQL پیشنهادی)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'construction_db',
        'USER': 'construction_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# تنظیمات Static Files
STATIC_ROOT = '/var/www/construction/static/'
MEDIA_ROOT = '/var/www/construction/media/'

# تنظیمات Cache (Redis پیشنهادی)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# تنظیمات Logging
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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/construction/django.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/var/log/construction/security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# تنظیمات Email (برای ارسال ایمیل‌های امنیتی)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

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
