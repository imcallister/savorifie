import datetime
from decimal import Decimal
from dateutil.parser import parse

from django.db import transaction

from accountifie.common.api import api_func

import sales.apiv1 as sales_api
import inventory.apiv1 as inventory_api
import products.apiv1 as products_api
from sales.models import Sale, UnitSale, ProceedsAdjustment
from utilities.channel_fees import FBA_fee
from fulfill.models import Fulfillment, FulfillLine

from reports.calcs.unfulfilled import unfulfilled


def _map_sku(amzn_sku):
    if amzn_sku == 'DL-Z7RL-OS4O':
        return 'BE3'
    else:
        return amzn_sku


def _FBA_start_date():
    loaded_thru = sales_api.sales_loaded_thru('AMZN', {})
    # take a buffer to reload
    return (loaded_thru + datetime.timedelta(days=-3)).isoformat()


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

        #unfulfilled_items = api_func('fulfill', 'unfulfilled', str(s.id), {})['unfulfilled_items']
        unfulfilled_items = unfulfilled(str(s.id), {})['unfulfilled_items']
        for label, quantity in unfulfilled_items.iteritems():
            fline_info = {}
            fline_info['inventory_item_id'] = inv_items[label]
            fline_info['quantity'] = quantity
            fline_info['fulfillment_id'] = fulfill_obj.id
            fline_obj = FulfillLine(**fline_info)
            fline_obj.save()
    return
