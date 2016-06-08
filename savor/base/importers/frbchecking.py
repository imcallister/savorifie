import os
import datetime
import pandas as pd
from dateutil.parser import parse

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext


import accountifie.gl.models
from savor.base.models import Cashflow
from accountifie.toolkit.forms import FileForm

DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')


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


def order_upload(request):

    form = FileForm(request.POST, request.FILES)

    if form.is_valid():
        upload = request.FILES.values()[0]
        file_name = upload._name
        file_name_with_timestamp = accountifie.toolkit.uploader.save_file(upload)
        dupes, new_entries = process_frb(file_name_with_timestamp)
        messages.success(request, 'Loaded FRB file: %d new entries and %d duplicate entries' %(new_entries, dupes))
        context = {}
        return render_to_response('base/uploaded.html', context, context_instance=RequestContext(request))
    else:
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the First Republic file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))


def process_frb(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    with open(incoming_name, 'U') as f:
        entries = pd.read_csv(f, skiprows=3).fillna(0)

    entries.rename(columns={'Transaction Number': 'external_id', 'Date': 'post_date', 'Description': 'description'}, inplace=True)
    entries['amount'] = entries['Amount Debit'] + entries['Amount Credit']
    entries['post_date'] = entries['post_date'].map(lambda x: parse(x).date().isoformat())

    existing_entry_ctr = 0
    new_entry_ctr = 0

    flds = ['post_date', 'amount', 'description', 'external_id']
    for idx in entries.index:
        checking_info = entries.loc[idx][flds].to_dict()
        checking_obj = Cashflow.objects.filter(external_id=checking_info['external_id']).first()

        if checking_obj:
            existing_entry_ctr += 1
        else:
            new_entry_ctr += 1
            cashflow_obj = Cashflow(**checking_info)
            cashflow_obj.ext_account = accountifie.gl.models.ExternalAccount.objects.get(gl_account__id='1001')
            cashflow_obj.save()

    return existing_entry_ctr, new_entry_ctr
