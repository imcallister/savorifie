import os

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect

from fulfill.models import WarehouseFulfill, ShippingCharge
import accountifie.common.uploaders
from accountifie.toolkit.forms import FileForm
import inventory.apiv1 as inventory_api

from .file_models.NC2 import NC2CSVModel
from accountifie.common.uploaders.upload_tools import order_upload
import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

def upload(request):
    processor = process_nc2
    return order_upload(request,
                        processor,
                        label=False)



def create_nc2_shippingcharge(wh_flf):
    if ShippingCharge.objects \
                     .filter(invoice_number=wh_flf.warehouse_pack_id) \
                     .count() > 0:
        return 'SHIPPING CHARGE ALREADY EXISTS'

    chg = {}
    shipper = wh_flf.shipping_type.shipper.id
    chg['shipper_id'] = inventory_api.shipper('IFS360', {})['id']
    chg['account'] = 'N/A'
    chg['tracking_number'] = wh_flf.tracking_number
    chg['invoice_number'] = wh_flf.warehouse_pack_id
    chg['ship_date'] = wh_flf.ship_date
    chg['charge'] = wh_flf.shipping_cost
    chg['fulfillment_id'] = wh_flf.fulfillment.id
    chg['order_related'] = True
    chg['comment'] = ''
    try:
        ShippingCharge(**chg).save()
        return 'SHIPPING CHARGE CREATED'
    except:
        return 'SHIPPING CHARGE SAVE FAILED'


def process_nc2(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    wh_records, errors = NC2CSVModel.import_data(data=open(incoming_name, 'rU'))
    wh_id = inventory_api.warehouse('NC2', {})['id']

    new_recs_ctr = 0
    exist_recs_ctr = 0
    errors_cnt = len(errors)

    for rec in wh_records:
        rec['warehouse_id'] = wh_id
        rec_obj = WarehouseFulfill.objects \
                                  .filter(warehouse_pack_id=rec['warehouse_pack_id']) \
                                  .first()
        if rec_obj:
            # if warehose fulfill object already exists ... skip to next one
            exist_recs_ctr += 1
        else:
            new_recs_ctr += 1
            rec_obj = WarehouseFulfill(**rec)
            rec_obj.save()

            if rec_obj.fulfillment:
                create_nc2_shippingcharge(rec_obj)

    summary_msg = 'Loaded NC2 file: %d new records, %d duplicate records, %d bad rows' \
                                    % (new_recs_ctr, exist_recs_ctr, errors_cnt)
    return summary_msg, errors
