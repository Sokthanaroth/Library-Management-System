"""
Django settings for library_project project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-a44-e!fl*v6_3@dsl9e=71&i9vh%c16e_ao$ikkps-m^tv4*fg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'ckeditor',
    'ckeditor_uploader',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',

    # Local apps
    'library_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'library_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Project-level template directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required by DRF browsable API
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'library_project.wsgi.application'


# Database
DATABASES = {
    "default": { 
        "ENGINE": "django.db.backends.mysql", 
        "NAME": "db_lms", 
        "USER": "root", 
        "PASSWORD": "", 
        "HOST": "127.0.0.1", 
        "PORT": "3306", 
    }
}


# Authentication settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use DB-backed sessions


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'library_app.validators.SpecialCharacterValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}


# Email configuration (Gmail example)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'sokthanarothel@gmail.com'
EMAIL_HOST_PASSWORD = 'ngnyxflnrghbbdeh'
DEFAULT_FROM_EMAIL = 'Library Management System <sokthanarothel@gmail.com>'

# Password reset settings
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour


# Jazzmin UI Customization
JAZZMIN_SETTINGS = {
    "site_title": "Library Management Admin",
    "site_header": "Library Dashboard",
    "site_brand": "Library Admin",
    "welcome_sign": "Welcome to Library Management System",
    "copyright": "LibraryApp Team",
    "search_model": ["library_app.Book", "library_app.Member"],
    "icons": {
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "library_app.Book": "fas fa-book",
        "library_app.Author": "fas fa-pen-nib",
        "library_app.Category": "fas fa-tags",
        "library_app.Member": "fas fa-id-card",
        "library_app.BorrowRecord": "fas fa-book-reader",
        "library_app.Reservation": "fas fa-calendar-check",
    },
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"app": "library_app"},
    ],
    "order_with_respect_to": ["library_app", "auth"],
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cosmo",
    "dark_mode_theme": "darkly",
    "navbar": "navbar-dark navbar-primary",
    "sidebar": "sidebar-dark-primary",
    "brand_colour": "navbar-primary",
    "accent": "accent-navy",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
    },
}


# CKEditor
CKEDITOR_UPLOAD_PATH = "uploads/"
