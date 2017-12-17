import os

from django.conf import settings

from accountifie.common.uploaders.upload_tools import order_upload
from accountifie.gl.models import ExternalAccount
from base.models import Cashflow

from .file_models.FRB import FRBCSVModel
import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')


def upload(request):
    processor = process_frb
    return order_upload(request,
                        processor,
                        label=False)


def process_frb(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    cf_records, errors = FRBCSVModel.import_data(data=open(incoming_name, 'rU'))
    
    new_recs_ctr = 0
    exist_recs_ctr = 0
    errors_cnt = len(errors)

    # HARDCODE
    ext_account = ExternalAccount.objects.get(gl_account__id='1001')

    for rec in cf_records:
        rec['amount'] = rec.pop('debit') + rec.pop('credit')
        rec_obj = Cashflow.objects \
                          .filter(post_date=rec['post_date']) \
                          .filter(amount=rec['amount']) \
                          .filter(external_id=rec['external_id']) \
                          .count()
        if rec_obj > 0:
            exist_recs_ctr += 1
        else:
            new_recs_ctr += 1
            rec['ext_account'] = ext_account
            rec['counterparty_id'] = 'unknown'
            rec_obj = Cashflow(**rec)
            rec_obj.save(update_gl=False)

    summary_msg = 'Loaded FRB file: %d new records, %d duplicate records, %d bad rows' \
                                    % (new_recs_ctr, exist_recs_ctr, errors_cnt)
    return summary_msg, errors
