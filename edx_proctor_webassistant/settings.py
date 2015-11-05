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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '92s%@1n2ebtk=wn)nrn+4s+drfvkextock5i41p%v860=vb0!f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


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
    'ws4redis',
    'rest_framework',
    'social.apps.django_app.default',

    'api',
    'ui',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

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
                'ws4redis.context_processors.default',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
                "django.core.context_processors.request",
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = '/login/sso_npoed-oauth2'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + '/static/'
STATICFILES_FINDERS = ('django.contrib.staticfiles.finders.FileSystemFinder',
                       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
                       'djangobower.finders.BowerFinder',
                       'pipeline.finders.PipelineFinder',)
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), '..', 'components/bower_components'),
)

# Bower settings
# https://github.com/nvbn/django-bower
BOWER_COMPONENTS_ROOT = BASE_DIR + '/components/'
BOWER_PATH = '/usr/local/bin/bower'

BOWER_INSTALLED_APPS = (
    'angular',
    'angular-route',
    'angular-animate',
    'angular-sanitize',
    'jquery',
    'bootstrap',
    'ng-table',
    'angular-bootstrap',
    'angular-translate',
    'angular-translate-storage-local',
    'angular-translate-loader-static-files',
)

# Pipeline
# PIPELINE_ENABLED = True
PIPELINE_DISABLE_WRAPPER = True
PIPELINE_CSS = {
    'css': {
        'source_filenames': (
            'css/*.css',
            'bootstrap/dist/css/bootstrap.min.css',
            'ng-table/dist/ng-table.css',
        ),
        'output_filename': 'css/styles.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
}
PIPELINE_JS = {
    'js': {
        'source_filenames': (
            'jquery/dist/jquery.min.js',
            'bootstrap/dist/js/bootstrap.js',
            'angular/angular.js',
            'angular-animate/angular-animate.min.js',
            'angular-route/angular-route.min.js',
            'angular-cookies/angular-cookies.min.js',
            'angular-sanitize/angular-sanitize.min.js',
            'ng-table/dist/ng-table.min.js',
            'angular-bootstrap/ui-bootstrap.js',
            'angular-translate/angular-translate.min.js',
            'angular-translate-storage-local/angular-translate-storage-local.min.js',
            'angular-translate-storage-cookie/angular-translate-storage-cookie.min.js',
            'angular-translate-loader-static-files/angular-translate-loader-static-files.min.js',
            'js/app/app.js',
            'js/app/common/services/websocket.js',
        ),
        'output_filename': 'js/app.js',
    }
}


# Websocket settings
# http://django-websocket-redis.readthedocs.org/en/latest/installation.html
#
WEBSOCKET_EXAM_CHANNEL = 'attempts'
WEBSOCKET_URL = '/ws/'
WS4REDIS_CONNECTION = {
    'host': 'localhost',
    'port': 6379,
    # 'db': 0,
    # 'password': 'verysecret',
}
WS4REDIS_EXPIRE = 5
WS4REDIS_PREFIX = 'ws'
WSGI_APPLICATION = 'ws4redis.django_runserver.application'
WS4REDIS_ALLOWED_CHANNELS = (
    'attempts'
)
WS4REDIS_HEARTBEAT = '--heartbeat--'

EDX_URL = "<EDX_URL>"

# social auth settings
AUTHENTICATION_BACKENDS = (
    'api.social_auth_backends.NpoedBackend',
    'django.contrib.auth.backends.ModelBackend',
)
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'api.pipeline.create_or_update_permissions',
    'social.pipeline.user.user_details'
)

SSO_NPOED_URL = "http://<SSO url>"
SOCIAL_AUTH_SSO_NPOED_OAUTH2_KEY = '<KEY>'
SOCIAL_AUTH_SSO_NPOED_OAUTH2_SECRET = '<SECRET>'
SOCIAL_NEXT_URL = '/'

COURSE_ID_SLASH_SEPARATED = True

GRAPPELLI_ADMIN_TITLE = u"Открытое образование"

try:
    from settings_local import *
except ImportError:
    print ('Local settings import error')

