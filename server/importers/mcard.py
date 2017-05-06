import os
import logging

from ofxparse import OfxParser

from django.conf import settings

from accountifie.common.uploaders.upload_tools import order_upload
from base.models import CreditCardTrans


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

logger = logging.getLogger('default')


def upload(request):
    processor = process_mastercard
    return order_upload(request,
                        processor,
                        label=False)


def process_mastercard(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    statement = OfxParser.parse(file(incoming_name)).account
    card_number = statement.account_id
    transactions = statement.statement.transactions

    trans_ids = [tr.id for tr in transactions]
    
    dupes = [tr.trans_id for tr in CreditCardTrans.objects.filter(trans_id__in=trans_ids)]
    
    errors = []
    dupes_ctr = len(dupes)
    new_trans_ctr = 0
    error_ctr = 0
    for t in [t for t in transactions if t.id not in dupes]:
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
            errors.append(str(e))
            error_ctr += 1

    summary_msg = 'Loaded mastercard file: %d new records, %d duplicate records, %d bad rows' \
                                    % (new_trans_ctr, dupes_ctr, error_ctr)
    return summary_msg, errors
