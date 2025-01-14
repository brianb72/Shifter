"""
Django settings for shifter project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import logging
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

# Not required when running in DEBUG mode, removes requirement for dev envs.
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(" ")

INTERNAL_IPS = [
    "127.0.0.1",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'tailwind',
    'theme',
    'shifter_auth',
    'shifter_files',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'shifter_auth.middleware.ensure_password_changed',
    'shifter_auth.middleware.activate_timezone',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shifter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'theme.context_processors.debug',
            ],
        },
    },
]

WSGI_APPLICATION = 'shifter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
db_option = os.environ.get("DATABASE", "sqlite").lower()
if db_option == "postgres":
    db_engine = "django.db.backends.postgresql"
    # Ensure environment variables are set for postgres
    if not os.environ.get("SQL_DATABASE"):
        raise ValueError("SQL_DATABASE environment variable not set.")
    if not os.environ.get("SQL_HOST"):
        raise ValueError("SQL_HOST environment variable not set.")
    if not os.environ.get("SQL_USER"):
        raise ValueError("SQL_USER environment variable not set.")
    if not os.environ.get("SQL_PASSWORD"):
        raise ValueError("SQL_PASSWORD environment variable not set.")

elif db_option == "sqlite":
    db_engine = "django.db.backends.sqlite3"
    db_path = os.path.join(BASE_DIR, "db", "db.sqlite3")
else:
    raise ValueError("Invalid database engine specified in environment. "
                     + "Must be either sqlite or postgres.")

DATABASES = {
    "default": {
        "ENGINE": db_engine,
        "NAME": os.environ.get("SQL_DATABASE", db_path),
        "USER": os.environ.get("SQL_USER"),
        "PASSWORD": os.environ.get("SQL_PASSWORD"),
        "HOST": os.environ.get("SQL_HOST", "db"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'UserAttributeSimilarityValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'MinimumLengthValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'CommonPasswordValidator'),
    },
    {
        'NAME': ('django.contrib.auth.password_validation.'
                 'NumericPasswordValidator'),
    },
]

log_level = os.getenv('DJANGO_LOG_LEVEL', 'INFO')
if log_level.upper() == "OFF":
    log_level = logging.CRITICAL + 1
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': log_level,
            'class': 'logging.FileHandler',
            'filename': '/var/log/shifter.log',
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': log_level,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': log_level,
            'propagate': False,
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.environ.get("TIMEZONE", "UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Tailwind Settings
TAILWIND_APP_NAME = 'theme'

# Shifter Settings
AUTH_USER_MODEL = "shifter_auth.User"
LOGIN_REDIRECT_URL = "shifter_files:index"
LOGIN_URL = "shifter_auth:login"
DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M',     # '2006-10-25 14:30'
]

SHIFTER_FULL_DOMAIN = os.environ.get("SHIFTER_FULL_DOMAIN",
                                     default="localhost:1337")

DEFAULT_EXPIRY_OFFSET = timedelta(weeks=2)

CRONJOBS = [
    ('*/59 * * * *', 'shifter_files.cron.delete_expired_files')
]
