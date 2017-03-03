import os

from django.conf import settings

from .file_models.FBA import FBACSVModel
import inventory.apiv1 as inventory_api
from fulfill.models import WarehouseFulfill

from accountifie.common.uploaders.upload_tools import order_upload
import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

def upload(request):
    processor = process_FBA
    return order_upload(request,
                        processor,
                        label=False)


def process_FBA(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    wh_records, errors = FBACSVModel.import_data(data=open(incoming_name, 'rU'))
    wh_id = inventory_api.warehouse('FBA', {})['id']

    new_recs_ctr = 0
    exist_recs_ctr = 0
    errors_cnt = len(errors)

    for rec in wh_records:
        rec['warehouse_id'] = wh_id
        rec_obj = WarehouseFulfill.objects \
                                  .filter(warehouse_pack_id=rec['warehouse_ship_id']) \
                                  .first()
        if rec_obj:
            # if warehose fulfill object already exists ... skip to next one
            exist_recs_ctr += 1
        else:
            new_recs_ctr += 1
            rec_obj = WarehouseFulfill(**rec)
            rec_obj.save()

            
    summary_msg = 'Loaded FBA fulfillments file: %d new records, %d duplicate records, %d bad rows' \
                                    % (new_recs_ctr, exist_recs_ctr, errors_cnt)
    return summary_msg, errors
