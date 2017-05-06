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
            'handlers': ['database', 'console'],
            'level': 'DEBUG',
            'propagate': True,
            },
        }
}

