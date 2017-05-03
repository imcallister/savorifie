import os
import sys
import traceback
from dateutil.parser import parse
from decimal import Decimal
import datetime

from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction


from .thirdparty_apis.amazon_sellercentral import load_orders, order_details
import sales.apiv1 as sales_api
import inventory.apiv1 as inventory_api
import products.apiv1 as products_api

from sales.models import Sale, UnitSale, ProceedsAdjustment
from accountifie.common.api import api_func
from utilities.channel_fees import FBA_fee
from fulfill.models import Fulfillment, FulfillLine
import fulfill.apiv1 as fulfill_api


import logging
logger = logging.getLogger('default')



def upload(request):
    try:
        summary_msg, error_msgs = load_FBA(request.user.username)
        return JsonResponse({'summary': summary_msg, 'errors': error_msgs})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        return JsonResponse({'summary': 'FBA upload failed on %s, %s' % (exc_type, exc_value), 'errors': []})

def _FBA_start_date():
    loaded_thru = sales_api.sales_loaded_thru('AMZN', {})
    # take a buffer to reload
    return (loaded_thru + datetime.timedelta(days=-3)).isoformat()



def _map_sku(amzn_sku):
    if amzn_sku == 'DL-Z7RL-OS4O':
        return 'BE3'
    else:
        return amzn_sku

def _create_unitsale(us):
    sku = _map_sku(us.get('SellerSKU'))
    try:
        sku_id = api_func('products', 'product', sku)['id']
        item_price = Decimal(us.get('ItemPrice', '0')) / Decimal(us.get('QuantityOrdered', '0'))
        return {'quantity': int(us.get('QuantityOrdered', '0')),
                'unit_price': item_price,
                'sku_id': sku_id}
    except:
        return


def _create_sale(order, order_details):
    sale_info = {}
    sale_info['company_id'] = 'SAV'
    sale_info['external_channel_id'] = order.get('AmazonOrderId')
    sale_info['paid_thru_id'] = 'AMZN'
    sale_info['shipping_name'] = order.get('ShippingAddress', {}).get('Name')
    sale_info['shipping_address1'] = order.get('ShippingAddress', {}).get('AddressLine1', '')
    sale_info['shipping_address2'] = order.get('ShippingAddress', {}).get('AddressLine2', '')
    sale_info['shipping_city'] = order.get('ShippingAddress', {}).get('City', '')
    sale_info['shipping_zip'] = order.get('ShippingAddress', {}).get('PostalCode', '')
    sale_info['shipping_province'] = order.get('ShippingAddress', {}).get('StateOrRegion', '')
    sale_info['shipping_country'] = order.get('ShippingAddress', {}).get('CountryCode', '')
    sale_info['sale_date'] = parse(order.get('PurchaseDate')).date()
    sale_info['channel_id'] = api_func('sales', 'channel', 'AMZN')['id']
    sale_info['customer_code_id'] = 'retail_buyer'
    return sale_info, [_create_unitsale(us) for us in order_details]

@transaction.atomic
def _save_objects(sale, unitsales, fulfill_channel):
    FBA_wh = inventory_api.warehouse('FBA', {})['id']
    FBA_shiptype = inventory_api.shippingtype('FBA', {})['id']
    inv_items = dict((i['label'], i['id']) for i in products_api.inventoryitem({}))

    s = Sale(**sale)
    s.save()
    for u in unitsales:
        if u:
            u['sale_id'] = s.id
            u['date'] = s.sale_date
            UnitSale(**u).save()

    pa = {}
    pa['amount'] = -FBA_fee(s)
    if pa['amount'] != Decimal('0'):
        pa['date'] = s.sale_date
        pa['sale_id'] = s.id
        pa['adjust_type'] = 'CHANNEL_FEES'
        ProceedsAdjustment(**pa).save()

    if fulfill_channel == 'AFN':
        fulfill_info = {}
        fulfill_info['request_date'] = s.sale_date
        fulfill_info['warehouse_id'] = FBA_wh
        fulfill_info['order_id'] = s.id
        fulfill_info['status'] = 'requested'
        fulfill_info['bill_to'] = 'AMZN'
        fulfill_info['ship_type_id'] = FBA_shiptype

        fulfill_obj = Fulfillment(**fulfill_info)
        fulfill_obj.save()

        unfulfilled_items = fulfill_api.unfulfilled(str(s.id), {})['unfulfilled_items']
        for label, quantity in unfulfilled_items.iteritems():
            fline_info = {}
            fline_info['inventory_item_id'] = inv_items[label]
            fline_info['quantity'] = quantity
            fline_info['fulfillment_id'] = fulfill_obj.id
            fline_obj = FulfillLine(**fline_info)
            fline_obj.save()
    return


def load_FBA(user, from_date=None):
    if not from_date:
        from_date = _FBA_start_date()

    orders = load_orders(from_date)
    orders_dict = dict((o.get('AmazonOrderId'), o) for o in orders)
    
    
    FBA_ids = [o.get('AmazonOrderId') for o in orders]
    existing_ids = [s['external_channel_id'] for s in Sale.objects.filter(external_channel_id__in=FBA_ids).values('external_channel_id')]
    
    new_ids = [o for o in FBA_ids if o not in existing_ids]
    cmplt_new_ids = [o for o in new_ids if orders_dict.get(o).get('OrderStatus') != 'Pending']
    new_order_ctr = 0
    bad_order_ctr = 0
    errors = []

    for o in cmplt_new_ids:
        try:
            od = order_details(o)
        except:
            logger.exception('Failed to get order details for AMZN order %s' % o)
            
        sale, unitsales = _create_sale(orders_dict.get(o), od)

        try:
            _save_objects(sale, unitsales, orders_dict.get(o).get('FulfillmentChannel'))
            logger.info('%s saved AMZN order %s' % (user, o))
            new_order_ctr += 1
        except:
            logger.exception('%s failed to save order and/or fulfillment for AMZN order %s' % (user, o))
            bad_order_ctr += 1
    
    summary_msg = 'Loaded FBA orders: %d new orders, %d bad orders' \
                                    % (new_order_ctr, bad_order_ctr)
    return summary_msg, errors
