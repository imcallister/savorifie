import os
import itertools

from django.conf import settings
from sales.models import Sale, UnitSale
from fulfill.models import Fulfillment, FulfillLine
from products.models import Product
import inventory.apiv1 as inventory_api
import products.apiv1 as products_api

from .file_models.AMZN_orders import AMZNOrdersCSVModel
from accountifie.common.uploaders.upload_tools import order_upload
from accountifie.common.api import api_func

import logging

logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

def upload(request):
    processor = process_AMZN_orders
    return order_upload(request,
                        processor,
                        label=False)



def process_AMZN_orders(file_name):
    if file_name.split('.')[-1] != 'txt':
        return {'status': 'ERROR', 'msg': 'WRONG_FILE_TYPE'}

    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    am_records, errors = AMZNOrdersCSVModel.import_data(data=open(incoming_name, 'rU'))
    
    sales_items = agg_amzn(am_records)

    FBA_wh = inventory_api.warehouse('FBA', {})['id']
    FBA_shiptype = inventory_api.shippingtype('FBA', {})['id']
    inv_items = dict((i['label'], i['id']) for i in products_api.inventoryitem({}))
    
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

            fulfilled_by = sale_info.pop('fulfilled_by')

            sale_info['channel_id'] = api_func('sales', 'channel', 'AMZN')['id']

            del sale_info['status']
            sale_info['customer_code_id'] = 'retail_buyer'
            sale_info['paid_thru_id'] = 'AMZN_PMTS'
            sale_obj = Sale(**sale_info)
            sale_obj.save()

            for us in s['unit_sales']:
                us['sale_id'] = sale_obj.id
                us['sku_id'] = Product.objects.get(label=us['sku']).id
                del us['sku']
                us_obj = UnitSale(**us)
                us_obj.date = sale_obj.sale_date
                us_obj.save()

            if fulfilled_by == 'AMZN':
                fulfill_info = {}
                fulfill_info['request_date'] = sale_obj.sale_date
                fulfill_info['warehouse_id'] = FBA_wh
                fulfill_info['order_id'] = sale_obj.id
                fulfill_info['status'] = 'requested'
                fulfill_info['bill_to'] = 'AMZN'
                fulfill_info['ship_type_id'] = FBA_shiptype

                fulfill_obj = Fulfillment(**fulfill_info)
                fulfill_obj.save()

                unfulfilled_items = api_func('fulfill', 'unfulfilled', str(sale_obj.id), {})['unfulfilled_items']
                for label, quantity in unfulfilled_items.iteritems():
                    fline_info = {}
                    fline_info['inventory_item_id'] = inv_items[label]
                    fline_info['quantity'] = quantity
                    fline_info['fulfillment_id'] = fulfill_obj.id
                    fline_obj = FulfillLine(**fline_info)
                    fline_obj.save()

    summary_msg = 'Loaded Amazon file: %d new records, %d duplicate records, %d bad rows' \
                                    % (new_sales_ctr, exist_sales_ctr, len(errors))
    
    return summary_msg, errors



def agg_amzn(records):
    am_records = [r for r in records if r['status'] != 'Cancelled']

    flds = ['status', 'shipping_charge', 'fulfilled_by',
            'shipping_city', 'shipping_zip',
            'shipping_province', 'shipping_country',
            'external_channel_id', 'sale_date']
          

    keyfunc = lambda x: x['external_channel_id']
    
    sale_items = []
    for k, g in itertools.groupby(sorted(am_records, key=keyfunc), keyfunc):
        sale_data = list(g)
        sale_info = dict((f, sale_data[0][f]) for f in flds)

        sale_info['gift_wrap_fee'] = sum(s['gift_wrap_fee'] for s in sale_data)
        sale_info['gift_wrapping'] = (sale_info['gift_wrap_fee'] > 0)

        us_flds = ['unit_price', 'quantity', 'sku']
        sale_info['unit_sales'] = [dict((uf, us[uf]) for uf in us_flds) for us in sale_data]
        sale_items.append(sale_info)
    
    return sale_items
