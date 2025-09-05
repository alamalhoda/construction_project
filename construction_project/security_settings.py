"""
تنظیمات امنیتی Django
Security Settings for Django Construction Project
"""

import os
from pathlib import Path

# تنظیمات امنیتی پایه
SECURITY_SETTINGS = {
    # تنظیمات HTTPS
    'SECURE_SSL_REDIRECT': True,
    'SECURE_HSTS_SECONDS': 31536000,  # 1 سال
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
    'SECURE_HSTS_PRELOAD': True,
    
    # تنظیمات Cookie
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Strict',
    'CSRF_COOKIE_SECURE': True,
    'CSRF_COOKIE_HTTPONLY': True,
    'CSRF_COOKIE_SAMESITE': 'Strict',
    
    # تنظیمات Content Security
    'SECURE_CONTENT_TYPE_NOSNIFF': True,
    'SECURE_BROWSER_XSS_FILTER': True,
    'X_FRAME_OPTIONS': 'DENY',
    
    # تنظیمات Referrer Policy
    'SECURE_REFERRER_POLICY': 'strict-origin-when-cross-origin',
    
    # تنظیمات CORS (اگر نیاز باشد)
    'CORS_ALLOW_CREDENTIALS': False,
    'CORS_ALLOW_ALL_ORIGINS': False,
}

# تنظیمات امنیتی برای Development
DEVELOPMENT_SECURITY_SETTINGS = {
    'SECURE_SSL_REDIRECT': False,
    'SESSION_COOKIE_SECURE': False,
    'CSRF_COOKIE_SECURE': False,
    'SECURE_HSTS_SECONDS': 0,
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': False,
    'SECURE_HSTS_PRELOAD': False,
    'SESSION_COOKIE_HTTPONLY': False,  # برای development
    'SESSION_COOKIE_SAMESITE': 'Lax',  # نرم‌تر از Strict
    'CSRF_COOKIE_HTTPONLY': False,  # برای development
    'CSRF_COOKIE_SAMESITE': 'Lax',  # نرم‌تر از Strict
    'SECURE_CONTENT_TYPE_NOSNIFF': False,  # برای development
    'SECURE_BROWSER_XSS_FILTER': False,  # برای development
    'X_FRAME_OPTIONS': 'SAMEORIGIN',  # نرم‌تر از DENY
    'SECURE_REFERRER_POLICY': 'no-referrer-when-downgrade',  # نرم‌تر
    # تنظیمات CSRF برای Codespace
    'CSRF_TRUSTED_ORIGINS': [
        'https://*.app.github.dev',
        'https://*.preview.app.github.dev',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'https://localhost:8000',
        'https://127.0.0.1:8000',
        'https://organic-winner-p649rx6xwxhr9r9-8000.app.github.dev',
    ],
}

# تنظیمات امنیتی برای Production
PRODUCTION_SECURITY_SETTINGS = {
    **SECURITY_SETTINGS,
    'DEBUG': False,
    'ALLOWED_HOSTS': [
        'localhost',
        '127.0.0.1',
        '.app.github.dev',
        '.preview.app.github.dev',
        'organic-winner-p649rx6xwxhr9r9-8000.app.github.dev',
        '*',
        # اضافه کردن دامنه‌های واقعی در production
        # 'yourdomain.com',
        # 'www.yourdomain.com',
    ],
    'CSRF_TRUSTED_ORIGINS': [
        'https://*.app.github.dev',
        'https://*.preview.app.github.dev',
        'https://organic-winner-p649rx6xwxhr9r9-8000.app.github.dev',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
        'https://localhost:8000',
        'https://127.0.0.1:8000',
    ],
}

# تنظیمات Password Security
PASSWORD_SECURITY_SETTINGS = {
    'AUTH_PASSWORD_VALIDATORS': [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 12,  # حداقل 12 کاراکتر
            }
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
            'OPTIONS': {
                'user_attributes': ('username', 'email', 'first_name', 'last_name'),
                'max_similarity': 0.7,
            }
        },
    ],
    
    # تنظیمات Session
    'SESSION_COOKIE_AGE': 3600,  # 1 ساعت
    'SESSION_EXPIRE_AT_BROWSER_CLOSE': True,
    'SESSION_SAVE_EVERY_REQUEST': True,
    
    # تنظیمات Login
    'LOGIN_REDIRECT_URL': '/api/dashboard/',
    'LOGIN_URL': '/login/',
    'LOGOUT_REDIRECT_URL': '/',
    
    # تنظیمات Password Reset
    'PASSWORD_RESET_TIMEOUT': 3600,  # 1 ساعت
}

# تنظیمات Logging امنیتی
SECURITY_LOGGING_SETTINGS = {
    'LOGGING': {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'security': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'security_file': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': 'logs/security.log',
                'formatter': 'security',
            },
            'security_console': {
                'level': 'ERROR',
                'class': 'logging.StreamHandler',
                'formatter': 'security',
            },
        },
        'loggers': {
            'django.security': {
                'handlers': ['security_file', 'security_console'],
                'level': 'WARNING',
                'propagate': True,
            },
            'django.request': {
                'handlers': ['security_file'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
    },
}

# تنظیمات Database Security
DATABASE_SECURITY_SETTINGS = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',  # بهتر از SQLite
            'NAME': os.environ.get('DB_NAME', 'construction_db'),
            'USER': os.environ.get('DB_USER', 'construction_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',  # اجباری کردن SSL
            },
        }
    },
    
    # تنظیمات Connection Pooling
    'CONN_MAX_AGE': 60,  # 1 دقیقه
}

# تنظیمات File Upload Security
FILE_UPLOAD_SECURITY_SETTINGS = {
    'FILE_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
    'DATA_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
    'DATA_UPLOAD_MAX_NUMBER_FIELDS': 1000,
    'FILE_UPLOAD_PERMISSIONS': 0o644,
    'FILE_UPLOAD_DIRECTORY_PERMISSIONS': 0o755,
}

# تنظیمات Cache Security
CACHE_SECURITY_SETTINGS = {
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PASSWORD': os.environ.get('REDIS_PASSWORD', ''),
            },
            'KEY_PREFIX': 'construction_project',
            'TIMEOUT': 300,  # 5 دقیقه
        }
    },
}

# تنظیمات Email Security
EMAIL_SECURITY_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
    'EMAIL_HOST': os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
    'EMAIL_PORT': int(os.environ.get('EMAIL_PORT', '587')),
    'EMAIL_USE_TLS': True,
    'EMAIL_USE_SSL': False,
    'EMAIL_HOST_USER': os.environ.get('EMAIL_HOST_USER', ''),
    'EMAIL_HOST_PASSWORD': os.environ.get('EMAIL_HOST_PASSWORD', ''),
    'DEFAULT_FROM_EMAIL': os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@construction.com'),
}

# تنظیمات Rate Limiting
RATE_LIMITING_SETTINGS = {
    'RATELIMIT_ENABLE': True,
    'RATELIMIT_USE_CACHE': 'default',
    'RATELIMIT_VIEW': 'django_ratelimit.views.ratelimit',
}

# تنظیمات Admin Security
ADMIN_SECURITY_SETTINGS = {
    'ADMIN_URL': 'admin/',  # تغییر URL ادمین از پیش‌فرض
    'ADMIN_SITE_HEADER': 'Construction Project Admin',
    'ADMIN_SITE_TITLE': 'Construction Admin',
    'ADMIN_INDEX_TITLE': 'Construction Project Administration',
}

def get_security_settings(environment='development'):
    """
    دریافت تنظیمات امنیتی بر اساس محیط
    
    Args:
        environment (str): 'development' یا 'production'
    
    Returns:
        dict: تنظیمات امنیتی
    """
    
    if environment == 'production':
        return {
            **PRODUCTION_SECURITY_SETTINGS,
            **PASSWORD_SECURITY_SETTINGS,
            **SECURITY_LOGGING_SETTINGS,
            **DATABASE_SECURITY_SETTINGS,
            **FILE_UPLOAD_SECURITY_SETTINGS,
            **CACHE_SECURITY_SETTINGS,
            **EMAIL_SECURITY_SETTINGS,
            **RATE_LIMITING_SETTINGS,
            **ADMIN_SECURITY_SETTINGS,
        }
    else:
        return {
            **DEVELOPMENT_SECURITY_SETTINGS,
            **PASSWORD_SECURITY_SETTINGS,
            **SECURITY_LOGGING_SETTINGS,
            **ADMIN_SECURITY_SETTINGS,
        }
