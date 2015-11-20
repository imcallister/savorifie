import datetime

import accountifie.gl.models


def exclude_mcard():
    return []


def unique_mcard(instance):
    if instance.__class__.objects.filter(description=instance.description, amount=instance.amount, post_date=instance.post_date):
        return False
    else:
        return instance


def clean_mcard_fields(field_name):
    return field_name


def clean_mcard_values(name, value):
    if name in ['post_date', 'trans_date']:
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