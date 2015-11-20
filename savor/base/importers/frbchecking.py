import datetime

import accountifie.gl.models


def exclude_frbchecking():
    return []


def unique_frbchecking(instance):
    if instance.__class__.objects.filter(post_date=instance.post_date, amount=instance.amount, external_id=instance.external_id):
        return False
    else:
        instance.ext_account = accountifie.gl.models.ExternalAccount.objects.get(gl_account__id='1001')
        return instance




def clean_frbchecking_fields(field_name):
    if field_name in ['memo', 'amount_debit', 'amount_credit', 'balance', 'check_number', 'fees__']:
        return None
    elif field_name == 'date':
        return 'post_date'
    elif field_name == 'transaction_number':
        return 'external_id'
    else:
        return field_name


def clean_frbchecking_values(name, value):
    if name == 'date':
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