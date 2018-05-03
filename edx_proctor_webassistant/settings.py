# -*- coding: utf-8 -*-
"""
Django settings for edx_proctor_webassistant project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TESTING = False
try:
    TESTING = sys.argv[1] == 'test'
except IndexError:
    pass

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

SECRET_KEY = '<ADD_YOUR_SECRET_KEY_IN_LOCAL_SETTINGS>'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'djangobower',
    'pipeline',
    'rest_framework',

    'person',
    'proctoring',
    'ui',
    'journaling',
    'social_django',
    'sso_auth',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'edx_proctor_webassistant.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/', ],
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

# WSGI_APPLICATION = 'edx_proctor_webassistant.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'ru'
if TESTING:
    LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

LOGIN_URL = LOGIN_REDIRECT_URL = LOGOUT_REDIRECT_URL = "/"

# Auth settings with/without sso
AUTH_BACKEND_NAME = 'sso_npoed-oauth2'
SSO_ENABLED = True

SSO_NPOED_URL = ''
PLP_NPOED_URL = ''

if SSO_ENABLED:
    TEMPLATES[0]['OPTIONS']['context_processors'] += [
        'social_django.context_processors.backends',
        'social_django.context_processors.login_redirect',
    ]
    try:
        from sso_auth.social_auth_settings import *
    except ImportError:
        print("CRITICAL: Social auth enabled. But  social_auth_settings.py didn't specified")
        exit()

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + '/static/'
STATICFILES_FINDERS = ('django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                       'djangobower.finders.BowerFinder',
                       'pipeline.finders.PipelineFinder',)
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), '..',
                 'components/bower_components'),
)

# Bower settings
# https://github.com/nvbn/django-bower
BOWER_COMPONENTS_ROOT = BASE_DIR + '/components/'

BOWER_INSTALLED_APPS = (
    'angular#1.6.10',
    'angular-translate#2.17.1',
    'angular-route#1.6.10',
    'angular-animate#1.6.10',
    'angular-sanitize#1.6.10',
    'angular-cookies#1.6.10',
    'angular-loading-bar#0.9.0',
    'jquery#3.1.1',
    'bootstrap#4.0.0',
    'moment#2.22.0',
    'git://github.com/dmitry-viskov/angular-data-grid.github.io.git#25561765d263669b8fd233155ad24c32ab0a68c3',
    'angular-bootstrap#2.5.0',
    'angular-translate-storage-local#2.17.1',
    'angular-translate-loader-static-files#2.17.1',
    'angular-translate-storage-cookie#2.17.1',
    'sockjs-client#1.1.4',
    'components-font-awesome#5.0.6'
)

# Pipeline

PIPELINE_ENABLED = False
FILE_POSTFIX = '.min'

# no compression because we use already minified files (FILE_POSTFIX = '.min')
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'

PIPELINE_DISABLE_WRAPPER = True
PIPELINE_CSS = {
    'css': {
        'source_filenames': (
            'bootstrap/dist/css/bootstrap' + FILE_POSTFIX + '.css',
            'components-font-awesome/css/fontawesome-all' + FILE_POSTFIX + '.css',
            'angular-loading-bar/build/loading-bar' + FILE_POSTFIX + '.css',
            'css/styles.css',
        ),
        'output_filename': 'css/bundle.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
}
PIPELINE_JS = {
    'js': {
        'source_filenames': (
            'jquery/dist/jquery' + FILE_POSTFIX + '.js',
            'moment/min/moment.min.js',
            'bootstrap/dist/js/bootstrap' + FILE_POSTFIX + '.js',
            'angular/angular' + FILE_POSTFIX + '.js',
            'angular-animate/angular-animate' + FILE_POSTFIX + '.js',
            'angular-route/angular-route' + FILE_POSTFIX + '.js',
            'angular-cookies/angular-cookies' + FILE_POSTFIX + '.js',
            'angular-sanitize/angular-sanitize' + FILE_POSTFIX + '.js',
            'angular-data-grid/dist/dataGrid' + FILE_POSTFIX + '.js',
            'angular-data-grid/dist/dataGridUtils' + FILE_POSTFIX + '.js',
            'angular-data-grid/dist/pagination' + FILE_POSTFIX + '.js',
            'angular-data-grid/dist/loading-bar' + FILE_POSTFIX + '.js',
            'angular-bootstrap/ui-bootstrap' + FILE_POSTFIX + '.js',
            'angular-translate/angular-translate' + FILE_POSTFIX + '.js',
            'angular-translate-storage-local/angular-translate-storage-local' + FILE_POSTFIX + '.js',
            'angular-translate-storage-cookie/angular-translate-storage-cookie' + FILE_POSTFIX + '.js',
            'angular-translate-loader-static-files/angular-translate-loader-static-files' + FILE_POSTFIX + '.js',
            'angular-loading-bar/build/loading-bar' + FILE_POSTFIX + '.js',
            'sockjs-client/dist/sockjs' + FILE_POSTFIX + '.js',
            'js/app.js',
            'js/lib/checklist-model.js',
            'js/app/common/modules/websocket.js',
            'js/app/common/modules/auth.js',
            'js/app/common/modules/backend_api.js',
            'js/app/common/modules/session.js',
            'js/app/common/modules/i18n.js',
            'js/app/common/modules/date.js',
            'js/app/common/services/exam_polling.js',
            'js/app/common/services/ws_data.js',
            'js/app/common/helpers.js',
            'js/app/ui/archive/archController.js',
            'js/app/ui/error/errController.js',
            'js/app/ui/home/hmController.js',
            'js/app/ui/home/hmDirectives.js',
            'js/app/ui/profile/pfController.js',
            'js/app/ui/sessions/rsController.js',
            'js/app/ui/sessions/rsDirectives.js',
        ),
        'output_filename': 'js/bundle.js',
    }
}

# Config for Single Page Application
SPA_CONFIG = {
    "sso_enabled": SSO_ENABLED,
    "language": "en",
    "allow_language_change": False,
    "supported_languages": ['en']
}

FINAL_ATTEMPT_STATUSES = ['error', 'verified', 'rejected', 'deleted_in_edx', 'declined', 'timed_out']

NOTIFICATIONS = {
    'DAEMON_ID': '1',
    'WEB_URL': '/notifications'
}

RAVEN_CONFIG = {}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(process)d '
                      '[%(name)s] %(filename)s:%(lineno)d - %(message)s',
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'server.log',
            'mode': 'w',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'notifications': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        }
    },
}


INSTRUCTOR_IS_PROCTOR = True

PROJECT_NAME = 'Web Assistant'
LOGO_NAME = 'img/epw-logo.png'  # may be URL


try:
    from .settings_local import *
except ImportError:
    print("CRITICAL: You must specify settings_local.py")
    exit()

INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django.raven_compat',
)
