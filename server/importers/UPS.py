import os
from itertools import groupby

from django.conf import settings

from accountifie.common.uploaders.upload_tools import order_upload

from fulfill.models import WarehouseFulfill, ShippingCharge
import inventory.apiv1 as inventory_api

from .file_models.UPS import UPSCSVModel
import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')


def agg_tracknum(tn_list):
    return {'ship_date': tn_list[0]['ship_date'],
            'invoice_number': tn_list[0]['invoice_number'],
            'account': tn_list[0]['account'],
            'charge': sum([s['charge'] for s in tn_list]),
            'tracking_number': tn_list[0]['tracking_number']}


def upload(request):
    processor = process_ups
    return order_upload(request,
                        processor,
                        label=False)


def process_ups(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    ship_charges, errors = UPSCSVModel.import_data(data=open(incoming_name, 'rU'),
                                                   skip_rows=6)
    shipper_id = inventory_api.shipper('UPS', {})['id']

    # group the data by unique tracking numbers
    ship_charges = sorted(ship_charges, key=lambda x: x['tracking_number'])
    gpd_ship_charges = groupby(ship_charges, key=lambda x: x['tracking_number'])
    aggd_ship_charges = [agg_tracknum(list(v)) for k, v in gpd_ship_charges]

    new_recs_ctr = 0
    exist_recs_ctr = 0
    errors_cnt = len(errors)

    for rec in aggd_ship_charges:
        rec['shipper_id'] = shipper_id
        rec['external_id'] = rec['tracking_number']
        rec_obj = ShippingCharge.objects \
                                .filter(external_id=rec['external_id']) \
                                .first()

        if rec_obj:
            # if warehose fulfill object already exists ... skip to next one
            exist_recs_ctr += 1
        else:
            whflf_obj = WarehouseFulfill.objects \
                                        .filter(tracking_number=rec['tracking_number']) \
                                        .first()
            if whflf_obj:
                flf = whflf_obj.fulfillment
                if flf:
                    rec['fulfillment_id'] = flf.id

            new_recs_ctr += 1
            rec_obj = ShippingCharge(**rec)
            rec_obj.save()

    summary_msg = 'Loaded UPS file: %d new records, \
                                    %d duplicate records, \
                                    %d bad rows' \
                                   % (new_recs_ctr, exist_recs_ctr, errors_cnt)
    return summary_msg, errors
