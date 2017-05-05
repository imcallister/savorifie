import os
from datetime import date

DATE_EARLY = date(2013,1,1)  #before anything in your accounts system
DATE_LATE = date(2099,1,1)  #after anything in your accounts system

# ACCOUNTIFIE SERVICE SETUP
ACCOUNTIFIE_SVC_URL = os.environ.get('ACCOUNTIFIE_SVC_URL', 'http://localhost:5124')
DEFAULT_GL_STRATEGY = os.environ.get('DEFAULT_GL_STRATEGY', 'remote')

TRACK_AJAX_CALLS = True
