from django.conf import settings
from os import path

DATA_ROOT = getattr(settings, 'DATA_DIR', 
                    path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = path.join(DATA_ROOT, 'processed')
ALLOWED_TYPES = [
    'mcard', 
    'checking',
    'saving', 
    'expense', 
    'checkingfrb',
]
