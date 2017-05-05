import os
from base import ENVIRON_DIR, BASE_DIR

try:
    from localsettings import LOCAL_DEBUG
    DEBUG = LOCAL_DEBUG
except ImportError:
    DEBUG = False


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


