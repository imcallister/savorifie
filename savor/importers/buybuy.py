import os
import itertools

from django.conf import settings
from sales.models import Sale, UnitSale
from products.models import Product

from .file_models.buybuy import BuyBuyCSVModel
from accountifie.common.uploaders.upload_tools import order_upload
from accountifie.common.api import api_func

import logging

logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

def upload(request):
    processor = process_buybuy
    return order_upload(request,
                        processor,
                        label=False)


def process_buybuy(file_name):
    if file_name.split('.')[-1] != 'csv':
        return {'status': 'ERROR', 'msg': 'WRONG_FILE_TYPE'}

    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    bb_records, errors = BuyBuyCSVModel.import_data(data=open(incoming_name, 'rU'),
                                                    skip_rows=4)
    
    sales_items = agg_buybuy(bb_records)
    
    new_sales_ctr = 0
    exist_sales_ctr = 0
    
    for s in sales_items:
        sale_obj = Sale.objects.filter(external_channel_id=s['external_channel_id']).first()

        if sale_obj:
            # if sale object already exists ... skip to next one
            exist_sales_ctr += 1
        else:
            new_sales_ctr += 1
            sale_info = dict((k, v) for k, v in s.iteritems() if k != 'unit_sales')
            sale_info['channel_id'] = api_func('sales', 'channel', sale_info['channel_label'])['id']
            del sale_info['channel_label']
            del sale_info['status']
            sale_obj = Sale(**sale_info)
            sale_obj.save()

            for us in s['unit_sales']:
                us['sale_id'] = sale_obj.id
                us['sku_id'] = Product.objects.get(label=us['sku']).id
                del us['sku']
                us_obj = UnitSale(**us)
                us_obj.date = sale_obj.sale_date
                us_obj.save()

    summary_msg = 'Loaded Buy Buy file: %d new records, %d duplicate records, %d bad rows' \
                                    % (new_sales_ctr, exist_sales_ctr, len(errors))
    
    return summary_msg, errors



def agg_buybuy(records):
    bb_records = [r for r in records if r['status'] != 'cancelled']

    flds = ['status', 'shipping_name', 'shipping_charge',
            'channel_label', 'shipping_city', 'shipping_zip',
            'shipping_province', 'shipping_phone', 'shipping_country',
            'external_channel_id', 'sale_date', 'shipping_address1',
            'shipping_address2', 'notification_email', 'customer_code_id',
            'shipping_company']
          

    keyfunc = lambda x: x['external_channel_id']
    
    sale_items = []
    for k, g in itertools.groupby(sorted(bb_records, key=keyfunc), keyfunc):
        sale_data = list(g)
        sale_info = dict((f, sale_data[0][f]) for f in flds)

        us_flds = ['unit_price', 'quantity', 'sku']
        sale_info['unit_sales'] = [dict((uf, us[uf]) for uf in us_flds) for us in sale_data]
        sale_items.append(sale_info)
    
    return sale_items

    """
    
    
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
    """
