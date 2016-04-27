from multipledispatch import dispatch

from accountifie.common.api import api_func
from inventory.models import *

def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data


