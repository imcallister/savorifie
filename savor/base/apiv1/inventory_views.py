import datetime

from django.conf import settings
from django.forms.models import model_to_dict

from savor.base.models import Sale, UnitSale


def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data


