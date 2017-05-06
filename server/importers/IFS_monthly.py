import os

from django.conf import settings


from .file_models.IFS_monthly import IFSMonthlyCSVModel
from fulfill.calcs import map_invoice_number
from accountifie.common.uploaders.upload_tools import order_upload

import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

def upload(request):
    processor = process_IFSmonthly
    return order_upload(request,
                        processor,
                        label=False)


def process_IFSmonthly(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    IFS_records, errors = IFSMonthlyCSVModel.import_data(data=open(incoming_name, 'rU'))
    
    invoice_assigments = {}
    for rec in IFS_records:
        if rec['warehouse_pack_id'] not in invoice_assigments and rec['invoice_id'] != '':
            invoice_assigments[rec['warehouse_pack_id']] = rec['invoice_id']

    records_mapped, error_cnt = map_invoice_number(invoice_assigments)

    summary_msg = 'Loaded IFS Monthly file: %d new records, %d bad rows' \
                                    % (records_mapped, error_cnt)
    return summary_msg, errors
