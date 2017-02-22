# Project project Django settings.
import os
import sys
import pandas

from django import get_version as django_version
from distutils.version import StrictVersion
DJANGO_19 = StrictVersion(django_version()) >= StrictVersion('1.9')
DJANGO_18 = not DJANGO_19


# CELERY SETUP
import djcelery
djcelery.setup_loader()
CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend'
BROKER_URL = 'redis://localhost:6379'
#CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['json', 'pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'json'

# stop those annoying warnings
pandas.options.mode.chained_assignment = None

# PATH SETUP
PROJECT_NAME = 'savor'
PROJECT_DIR = os.path.realpath(os.path.dirname(__file__))
sys.path.append(PROJECT_DIR)
ENVIRON_DIR = os.path.realpath(os.path.join(PROJECT_DIR, '..'))
CLIENT_PROJECT = os.path.split(ENVIRON_DIR)[1]


# ACCOUNTIFIE SERVICE SETUP
ACCOUNTIFIE_SVC_URL = os.environ.get('ACCOUNTIFIE_SVC_URL', 'http://localhost:5124')
DEFAULT_GL_STRATEGY = os.environ.get('DEFAULT_GL_STRATEGY', 'remote')


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
    from localsettings import DB_NAME
except ImportError:
    DB_NAME = 'accountifie'
try:
    from localsettings import DB_USER
except ImportError:
    DB_USER = 'accountifie'
try:
    from localsettings import DB_PASSWORD
except ImportError:
    DB_PASSWORD = ''

try:
    from localsettings import DB_HOST
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

# REACT/WEBPACK SETUP
if DEBUG:
    WEBPACK_LOADER = {
        'DEFAULT': {
            'BUNDLE_DIR_NAME': 'bundles/',
            'STATS_FILE': os.path.join(ENVIRON_DIR, 'webpack-stats.local.json'),
        }
    }
else:
    WEBPACK_LOADER = {
        'DEFAULT': {
            'BUNDLE_DIR_NAME': 'dist/',
            'STATS_FILE': os.path.join(ENVIRON_DIR, 'webpack-stats.prod.json'),
        }
    }


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

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
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

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_=s8f!l_t=ys+nbm3q%08ew8zb(7bybf195*rl2dil87p197g$'


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


##  OLD TEMPLATES

# List of callables that know how to import templates from various sources.
"""
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "accountifie.common.views.base_templates",

    "base.views.company_context",
    )

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),
    
)
"""
## END OF OLD TEMPLATES


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
    'simple_history.middleware.HistoryRequestMiddleware',
    'accountifie.toolkit.error_handling.StandardExceptionMiddleware',
)




ROOT_URLCONF = PROJECT_NAME + '.urls'
WSGI_APPLICATION = PROJECT_NAME + '.wsgi.application'


INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'djangosecure',
    'accountifie.dashboard',

    'djangobower',
    'webpack_loader',
    
    #'django_nose',
    'django_extensions',
    'simple_history',

    'djcelery',
    
    'betterforms',
    'base',
    'products',
    'sales',
    'inventory',
    'fulfill',
    'reports',
    'accounting',
    'importers',
    'testsuite',


    'accountifie.celery',
    'accountifie.common',
    'accountifie.forecasts',
    'accountifie.gl',
    'accountifie.snapshot',
    'accountifie.environment',
    'accountifie.reporting',
    'accountifie.cal',

    'dal',
    'dal_select2',
    'django_admin_bootstrapped',

    'django.contrib.admin',
    'django.contrib.admindocs',
    #'django_bootstrap_typeahead',
    #'django_graphiql',
    #'graphene.contrib.django',    
    'debug_toolbar',
    'django_behave',

    'rest_framework',
    
)

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
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s',
        },
        },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
            }
        },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
            },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        'database': {
            'level': 'INFO', # i.e., allows for logging messages of level INFO or higher
            'class': 'accountifie.common.log.DbLogHandler'
            }
        },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        'default': {
            'handlers': ['database', 'console'] if DEBUG or DEVELOP else ['database',],
            'level': 'DEBUG',
            'propagate': True,
            },
        }
}


#From cerberos
MAX_FAILED_LOGINS = 5
MEMORY_FOR_FAILED_LOGINS = 3600  #try again an hour later

#from django-passwords
PASSWORD_MIN_LENGTH = 8
PASSWORD_COMPLEXITY = { "DIGITS": 1, "UPPER": 1 }

#uncomment this or put in your local settings if you want to save rml
SAVERML = os.path.join(PROJECT_DIR,'latest.rml')

TRACK_AJAX_CALLS = True

TESTING = 'test' in sys.argv

try:
    from localsettings import *
except ImportError:
    pass

#recommendations for security from: http://django-secure.readthedocs.org/en/v0.1.2/
SECURE_SSL_REDIRECT = not DEVELOP   
SECURE_HSTS_SECONDS = 24*24*3600*30
SECURE_HSTS_SECONDS_INCLUDE_SUBDOMAINDS = True
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = not DEVELOP
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600

#avoids hourly logout when you're working
SESSION_SAVE_EVERY_REQUEST = True

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


from datetime import date
DATE_EARLY = date(2013,1,1)  #before anything in your accounts system
DATE_LATE = date(2099,1,1)  #after anything in your accounts system