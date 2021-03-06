"""
Django settings for project_meta_transform project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import urllib.parse
from pymongo import MongoClient

# from iqserviceplugins.configuration.env_servicer import ENVServicer

# ENVServicer.set_alps_service_env()


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3v(1=f*hr%uy=)3_02*d)jd-29tv=ubzhw7021th6qzo^i!rzu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS += ['apps.base_app']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'



# Cache Settings
ALPS_PROJECT_CACHE_KEY = 'ALPS_PROJECT_%s_%s'

# Activity/Error Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "{'time':'%(asctime)s','log_level':'%(levelname)s','raised_at':'%(module)s:%(lineno)s','message':'%(message)s'}",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'activity': {
            'format': '%(levelname)s|%(asctime)s|%(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'standalone_activity': {
            'format': '%(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/logs/ALPS.log',
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'activity.transform': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/tmp/logs/activity/transform.log',
            'formatter': 'activity'
        },
        'error.transform': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/tmp/logs/error/transform.error.log',
            'formatter': 'activity'
        }
    },
    'loggers': {
        'Logging': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'activity.transform': {
            'handlers': ['activity.transform'],
            'propagate': True,
            'level': 'INFO'
        },
        'error.transform': {
            'handlers': ['error.transform'],
            'propagate': True,
            'level': 'ERROR'
        }
    }
}

AWS_REGION = 'us-east-1'
AWS_ACCESS_KEY = 'AKIAY5S5RI75CQTJSTP6'
AWS_SECRET_KEY = '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'

os.environ['DC_AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY  # required for storage class connections
os.environ['DC_AWS_REGION'] = AWS_REGION
os.environ['DC_AWS_SECRET_KEY'] = AWS_SECRET_KEY


PROJECT_KW_URL_METADATA_COLLECTION_NAME = 'project_keyword_url_metadata_1'
