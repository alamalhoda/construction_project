"""
Django settings for construction_project project.

For more information on this file, see
https://docs.djangoproject.com/

"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^l)7d*%h&db4uft@dk%h-w&nup#pu%)a!d)c7jwgoixo5_hm0$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1',
    '.app.github.dev',
    '.preview.app.github.dev',
    'organic-winner-p649rx6xwxhr9r9-8000.app.github.dev',
    '*'
]

# تنظیمات امنیتی
from .security_settings import get_security_settings

# تشخیص محیط (development/production)
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

# اعمال تنظیمات امنیتی
security_config = get_security_settings(ENVIRONMENT)
locals().update(security_config)

# تنظیمات CSRF نرم‌تر برای development
CSRF_COOKIE_AGE = 3600  # 1 ساعت
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False  # برای JavaScript access
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False  # برای development
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
CSRF_TRUSTED_ORIGINS = [
    'https://*.app.github.dev',
    'https://*.preview.app.github.dev',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
    'https://organic-winner-p649rx6xwxhr9r9-8000.app.github.dev',
    'http://*.app.github.dev',
    'http://*.preview.app.github.dev',
]

# تنظیمات Content Security Policy بر اساس محیط
if DEBUG:
    # Development: CSP غیرفعال - همه فونت‌ها مجاز
    CSP_DEFAULT_SRC = None
    CSP_SCRIPT_SRC = None
    CSP_STYLE_SRC = None
    CSP_FONT_SRC = None
    CSP_IMG_SRC = None
    CSP_CONNECT_SRC = None
    CSP_FRAME_SRC = None
else:
    # Production: CSP فعال با تنظیمات مناسب برای فونت‌های base64
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

# تنظیمات Middleware بر اساس محیط
if DEBUG:
    # Development: CSP middleware غیرفعال
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',  # فعال برای امنیت
        'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise برای static files
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',

        # Middleware های امنیتی سفارشی (فعال با تنظیمات نرم‌تر برای development)
        'construction.security_middleware.SecurityHeadersMiddleware',
        'construction.security_middleware.AuditLogMiddleware',
        'construction.security_middleware.AdminSecurityMiddleware',
        'construction.security_middleware.LoginAttemptMiddleware',
        # Middleware های کاربران (موقتاً غیرفعال)
        # 'construction.user_middleware.UserAuthenticationMiddleware',
        # 'construction.user_middleware.UserSessionMiddleware',
    ]
else:
    # Production: CSP middleware فعال
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',  # فعال برای امنیت
        'whitenoise.middleware.WhiteNoiseMiddleware',  # Whitenoise برای static files
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',

        # Middleware های امنیتی سفارشی (فعال با تنظیمات نرم‌تر برای development)
        'construction.security_middleware.SecurityHeadersMiddleware',
        'construction.security_middleware.AuditLogMiddleware',
        'construction.security_middleware.AdminSecurityMiddleware',
        'construction.security_middleware.LoginAttemptMiddleware',
        # Middleware های کاربران (موقتاً غیرفعال)
        # 'construction.user_middleware.UserAuthenticationMiddleware',
        # 'construction.user_middleware.UserSessionMiddleware',
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
                'construction_project.context_processors.project_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'construction_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# تنظیمات دیتابیس
if os.environ.get('USE_SQLITE', 'true').lower() == 'true':
    # استفاده از SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.environ.get('DB_NAME', 'database/db.sqlite3'),
        }
    }
else:
    # استفاده از PostgreSQL (برای production)
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


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

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
WHITENOISE_AUTOREFRESH = True
WHITENOISE_MANIFEST_STRICT = False  # برای فایل‌های گمشده سخت‌گیر نباشد

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# تنظیمات پروژه سفارشی
PROJECT_TITLE = os.environ.get('PROJECT_TITLE', '🏗️ سیستم مدیریت مالی پروژه های آرشا')
PROJECT_DESCRIPTION = os.environ.get('PROJECT_DESCRIPTION', 'به سیستم مدیریت پروژه‌های ساختمانی خوش آمدید')
PROJECT_LOGO = os.environ.get('PROJECT_LOGO', '')  # مسیر لوگو - اختیاری
PROJECT_LOGO_ALT = os.environ.get('PROJECT_LOGO_ALT', 'لوگوی پروژه')  # متن جایگزین لوگو

LANGUAGE_CODE = 'fa-ir'

# تنظیمات زمان
TIME_ZONE = 'Asia/Tehran'
USE_TZ = True
USE_I18N = True
USE_L10N = True

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
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
