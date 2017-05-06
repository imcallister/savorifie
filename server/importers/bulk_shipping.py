import os

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect

from fulfill.models import WarehouseFulfill, ShippingCharge
from accountifie.toolkit.forms import FileForm

from .file_models.bulk_shipping import BulkShippingCSVModel
from fulfill.calcs import create_frank_shippingcharge
from accountifie.common.uploaders.upload_tools import order_upload
import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

def upload(request):
    processor = process_bulk_shipping
    return order_upload(request,
                        processor,
                        label=False)


def process_bulk_shipping(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    sh_records, errors = BulkShippingCSVModel.import_data(data=open(incoming_name, 'rU'))
    
    new_recs_ctr = 0
    exist_recs_ctr = 0
    errors_cnt = len(errors)
    
    for rec in sh_records:
        rec_obj = ShippingCharge.objects \
                               .filter(external_id=rec['external_id']) \
                               .first()
        if rec_obj:
            # if shipping charge object already exists update it
            exist_recs_ctr += 1
            for fld in ['shipper', 'external_id', 'tracking_number', 'invoice_number', 
                        'ship_date', 'charge', 'fulfillment', 'order_related']:
                setattr(rec_obj, fld, rec[fld])
            rec_obj.save()
        else:
            new_recs_ctr += 1
            rec_obj = ShippingCharge(**rec)
            rec_obj.save()
            
    summary_msg = 'Loaded bulk shipping charge file: %d new records, %d duplicate records, %d bad rows' \
                                    % (new_recs_ctr, exist_recs_ctr, errors_cnt)
    return summary_msg, errors
