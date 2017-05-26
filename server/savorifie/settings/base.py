# Project project Django settings.
import os
import sys
import pandas

from django import get_version as django_version
from distutils.version import StrictVersion
DJANGO_19 = StrictVersion(django_version()) >= StrictVersion('1.9')
DJANGO_18 = not DJANGO_19



# stop those annoying warnings
pandas.options.mode.chained_assignment = None

# PATH SETUP
PROJECT_NAME = 'server'

BASE_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
PROJECT_DIR = os.path.join(BASE_DIR, PROJECT_NAME)
#PROJECT_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(PROJECT_DIR)
ENVIRON_DIR = os.path.realpath(os.path.join(PROJECT_DIR, '..'))
CLIENT_PROJECT = os.path.split(ENVIRON_DIR)[1]


ROOT_URLCONF = PROJECT_NAME + '.savorifie.urls'
WSGI_APPLICATION = PROJECT_NAME + '.savorifie.wsgi.application'



# DEBUG SETTINGS
try:
    from localsettings import LOCAL_DEBUG
    DEBUG = LOCAL_DEBUG
    DEVELOP = LOCAL_DEBUG
except ImportError:
    DEBUG = False
    DEVELOP = False

TEMPLATE_DEBUG = False

# DATABASE SETTINGS
try:
    from db import DB_NAME
except ImportError:
    DB_NAME = 'accountifie'
try:
    from db import DB_USER
except ImportError:
    DB_USER = 'accountifie'
try:
    from db import DB_PASSWORD
except ImportError:
    DB_PASSWORD = ''

try:
    from db import DB_HOST
except ImportError:
    DB_HOST = 'localhost'

# override database variables" line="{{ item }}"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': '',
        'OPTIONS': {}
    },
}

# TEST SETTINGS
if 'test' in sys.argv or 'test_coverage' in sys.argv: #Covers regular testing and django-coverage
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

TEST_RUNNER = 'django_behave.runner.DjangoBehaveTestSuiteRunner'

ADMINS = (
    ('savor', 'ian@savor.us'),
)

MANAGERS = ADMINS
#Required for Django 1.5+.  Otherwise live servers in non-debug mode complain.
#It checks host headers against this list.
#ALLOWED_HOSTS = [CLIENT_PROJECT, '.savor.us']

ALLOWED_HOSTS = ['*']

if DEVELOP:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])



TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(ENVIRON_DIR, 'media')
DATA_ROOT = os.path.join(ENVIRON_DIR, 'data')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'
DATA_URL = '/data/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ENVIRON_DIR, 'htdocs', 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_DIR, 'components')

LOGO = 'base/img/savor_logo.png'
SITE_TITLE = 'savorifie'

PDFOUT_PATH = 'pdfout'
PDFOUT = os.path.join(DATA_ROOT, PDFOUT_PATH)


# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'static'),
    os.path.join(ENVIRON_DIR, 'assets')
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
)



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "accountifie.common.views.base_templates",
                "base.views.company_context",
            ],
        },
    },
]


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accountifie.middleware.docengine.UserFindingMiddleware',
    'djangosecure.middleware.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accountifie.middleware.ssl.SSLRedirect',
    'accountifie.toolkit.error_handling.StandardExceptionMiddleware',
)



REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5
}

BOWER_INSTALLED_APPS = (
    'jquery#1.11',
    'bootstrap',
    'bootstrap-table#1.9.0',
    'highcharts',

)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.


#uncomment this or put in your local settings if you want to save rml
SAVERML = os.path.join(PROJECT_DIR,'latest.rml')


TESTING = 'test' in sys.argv


from django.contrib import messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-debug',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger error'
    }


DASHBOARD_TITLE = CLIENT_PROJECT + ' Dashboard'
THUMBNAIL_SIZES = (
    (120,80),
    (240,160),
    (320,240),
    )

