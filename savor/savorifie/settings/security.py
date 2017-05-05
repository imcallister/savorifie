try:
    from localsettings import LOCAL_DEBUG
    DEVELOP = LOCAL_DEBUG
except ImportError:
    DEVELOP = False

# OVER-RIDE Amazon MWS Settings line="{{ item }}"


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

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_=s8f!l_t=ys+nbm3q%08ew8zb(7bybf195*rl2dil87p197g$'

#From cerberos
MAX_FAILED_LOGINS = 5
MEMORY_FOR_FAILED_LOGINS = 3600  #try again an hour later

#from django-passwords
PASSWORD_MIN_LENGTH = 8
PASSWORD_COMPLEXITY = { "DIGITS": 1, "UPPER": 1 }
