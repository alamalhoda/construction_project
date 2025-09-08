"""
Django settings for construction_project project.

For more information on this file, see
https://docs.djangoproject.com/

This file contains production settings optimized for Chabokan.net hosting.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '^l)7d*%h&db4uft@dk%h-w&nup#pu%)a!d)c7jwgoixo5_hm0$')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.chabokan.net',  # Chabokan domain
    '.chabokan.ir',   # Alternative Chabokan domain
    os.environ.get('ALLOWED_HOST', 'localhost'),  # Custom domain from environment
]

# تنظیمات امنیتی
from .security_settings import get_security_settings

# تشخیص محیط
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

# اعمال تنظیمات امنیتی
security_config = get_security_settings(ENVIRONMENT)
locals().update(security_config)

# تنظیمات CSRF
CSRF_COOKIE_AGE = 3600  # 1 ساعت
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_HTTPONLY = os.environ.get('CSRF_COOKIE_HTTPONLY', 'False').lower() == 'true'
CSRF_COOKIE_SAMESITE = os.environ.get('CSRF_COOKIE_SAMESITE', 'Lax')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else []

# تنظیمات Content Security Policy برای production
CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "data:", "blob:")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https:", "http:")
CSP_FONT_SRC = ("'self'", "https:", "http:", "data:", "blob:")
CSP_IMG_SRC = ("'self'", "data:", "https:", "http:")
CSP_CONNECT_SRC = ("'self'", "https:", "http:")
CSP_FRAME_SRC = ("'self'", "https:", "http:")

# تنظیمات احراز هویت
AUTHENTICATION_BACKENDS = [
    'construction.authentication.EnhancedAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_jalali",  # Place this before your custom apps
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

    'construction.apps.ConstructionConfig',  # استفاده از apps.py
    'dashboard',
    'backup',
    'django_extensions',
]

JALALI_SETTINGS = {
    # JavaScript static files for the admin Jalali date widget
    "ADMIN_JS_STATIC_FILES": [
        "admin/jquery.ui.datepicker.jalali/scripts/jquery-1.10.2.min.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js",
        "admin/jquery.ui.datepicker.jalali/scripts/calendar.all.js",
        "admin/jquery.ui.datepicker.jalali/scripts/calendar.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js",
        "admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js",
        "admin/main.js",
    ],
    # CSS static files for the admin Jalali date widget
    "ADMIN_CSS_STATIC_FILES": {
        "all": [
            "admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css",
            "admin/css/main.css",
        ]
    },
}

# Production Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise برای static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Middleware های امنیتی سفارشی
    'construction.security_middleware.SecurityHeadersMiddleware',
    'construction.security_middleware.AuditLogMiddleware',
    'construction.security_middleware.AdminSecurityMiddleware',
    'construction.security_middleware.LoginAttemptMiddleware',
]

ROOT_URLCONF = 'construction_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'construction_project.wsgi.application'

# Database configuration
# Use SQLite for development, PostgreSQL for production
if os.environ.get('USE_SQLITE', 'true').lower() == 'true':
    # SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'database' / os.environ.get('DB_FILE', 'db.sqlite3'),
        }
    }
else:
    # PostgreSQL for production (Chabokan.net)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'construction_db'),
            'USER': os.environ.get('DB_USER', 'construction_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'prefer',  # برای اتصال امن‌تر
            },
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# اضافه کردن پوشه static به STATICFILES_DIRS
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# تنظیمات Whitenoise برای static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# تنظیمات اضافی Whitenoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = False  # در production غیرفعال
WHITENOISE_MANIFEST_STRICT = True  # در production سخت‌گیر

# Media files (if needed)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# Logging configuration for production
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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'construction': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session settings
SESSION_COOKIE_SECURE = False if DEBUG else True  # برای development نرم‌تر
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 3600  # 1 hour

# Cache settings (if Redis is available)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email settings (configure with Chabokan email service)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.chabokan.net')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@chabokan.net')