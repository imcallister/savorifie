import datetime

import accountifie.gl.models


def exclude_jpmchecking():
    return []


def unique_jpmchecking(instance):
    if instance.__class__.objects.filter(post_date=instance.post_date, amount=instance.amount, description=instance.description):
        return False
    else:
        instance.ext_account = core.gl.models.ExternalAccount.objects.get(gl_account__id='1001')
        return instance

def clean_jpmchecking_fields(field_name):
    '''function to manually clean some known problems with field name to model attributes conversions,
            to be used internally by _utils.save_data
        Should always return a value'''
    if field_name in ['type', 'check_or_slip']:
        return None
    else:
        return field_name

def clean_jpmchecking_values(name, value):
    if name == 'post_date':
        month, day, year = value.split('/')
        if len(year) == 2:
            year = int('20%s' % year)
        else:
            year = int(year)
        return datetime.date(year, int(month), int(day)).isoformat()
    elif name == 'amount':  #remove commas in csv input
        value = value.replace(',', '')
        return value
    else:
        return value