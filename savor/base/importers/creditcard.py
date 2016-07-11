import os
import logging

from ofxparse import OfxParser

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from accountifie.toolkit.forms import FileForm
import accountifie.toolkit
from base.models import CreditCardTrans

DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

logger = logging.getLogger('default')


def ccard_upload(request):
    form = FileForm(request.POST, request.FILES)

    if form.is_valid():
        upload = request.FILES.values()[0]
        file_name = upload._name
        file_name_with_timestamp = accountifie.toolkit.uploader.save_file(upload)
        dupes, new_charges, errors = process_mastercard(file_name_with_timestamp)
        messages.success(request, 'Loaded mastercard file: %d new charges and %d duplicate charges' % (new_charges, dupes))
        messages.warning(request, 'Errors: %d.' % errors)
        context = {}
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the mastercard file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))


def process_mastercard(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    statement = OfxParser.parse(file(incoming_name)).account
    card_number = statement.account_id
    transactions = statement.statement.transactions

    trans_ids = [tr.id for tr in transactions]
    dupes = [tr.trans_id for tr in CreditCardTrans.objects.filter(trans_id__in=trans_ids)]

    dupes_ctr = len(dupes)
    new_trans_ctr = 0
    error_ctr = 0
    for t in [t for t in transactions if tr.id not in dupes]:
        if 'AUTOPAY' in t.payee:
            # these will show up in bank cashflow
            # don't want them double-entered
            continue

        # these should all be new
        try:
            trans_info = {}
            trans_info['card_company_id'] = 'MCARD'
            trans_info['counterparty_id'] = 'unknown'
            trans_info['trans_date'] = t.date
            trans_info['post_date'] = t.date
            trans_info['trans_type'] = t.type
            trans_info['trans_id'] = t.id

            trans_info['payee'] = t.payee
            trans_info['amount'] = t.amount
            trans_info['description'] = t.mcc
            if t.memo != '':
                trans_info['description'] += ': %s' % t.memo

            trans_info['card_number'] = card_number

            trans_obj = CreditCardTrans(**trans_info)
            trans_obj.save()
            new_trans_ctr += 1
        except Exception, e:
            logger.info(str(e))
            error_ctr += 1

    return dupes_ctr, new_trans_ctr, error_ctr
