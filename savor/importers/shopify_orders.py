import os
import sys
import traceback
from dateutil.parser import parse
from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction

from .thirdparty_apis.shopify_api import load_orders
import sales.apiv1 as sales_api
from sales.models import Sale, UnitSale, ProceedsAdjustment
from accountifie.common.api import api_func

from utilities.channel_fees import shopify_fee

import logging
logger = logging.getLogger('default')


PAID_THRU = {
    'shopify_payments': 'SHOPIFY',
    'paypal': 'PAYPAL',
    'amazon_payments': 'AMZN_PMTS'
}


def upload(request):
    summary_msg, error_msgs = load_shopify()
    return JsonResponse({'summary': summary_msg, 'errors': error_msgs})

def _Shopify_start_date():
    return sales_api.sales_loaded_thru('SHOPIFY', {}).isoformat()



def _create_unitsale(us):
    sku_id = api_func('products', 'product', us.sku)['id']
    return {'quantity': us.quantity,
            'unit_price': Decimal(us.price),
            'sku_id': sku_id}
    
def _create_taxlines(tl):
    try:
        tax_collector, created = TaxCollector.objects.get_or_create(entity=tl.title)
        return {'collector_id': tax_collector.id,
               'tax': Decimal(tl.price)}
    except:
        logging.error('Problem with tax line, %s' % str(tl))
        return None


def _create_sale(order):
    sale_info = {}
    sale_info['company_id'] = 'SAV'
    sale_info['external_channel_id'] = order.name
    
    sale_info['paid_thru_id'] = PAID_THRU.get(order.gateway)
    sale_info['shipping_name'] = order.shipping_address.name
    sale_info['shipping_company'] = order.shipping_address.company
    sale_info['shipping_address1'] = order.shipping_address.address1
    sale_info['shipping_address2'] = order.shipping_address.address2
    sale_info['shipping_city'] = order.shipping_address.city
    sale_info['shipping_zip'] = order.shipping_address.zip
    sale_info['shipping_province'] = order.shipping_address.province_code
    sale_info['shipping_country'] = order.shipping_address.country
    sale_info['sale_date'] = parse(order.created_at).date()
    sale_info['channel_id'] = api_func('sales', 'channel', 'SHOPIFY')['id']
    sale_info['customer_code_id'] = 'retail_buyer'
    sale_info['checkout_id'] = order.checkout_id
    sale_info['notification_email'] = order.email

    sale_info['discount'] = Decimal(order.total_discounts)
    sale_info['shipping_charge'] = sum(Decimal(sl.price) for sl in order.shipping_lines)

    # gift wrapping
    gw = [li for li in order.line_items if li.sku == 'GW001']
    if len(gw) > 0:
        sale_info['gift_wrapping'] = True
        sale_info['gift_wrap_fee'] = Decimal(gw[0].price)

    gift_msg_attrs = [a.value for a in order.note_attributes if a.name == 'gift-note']
    if len(gift_msg_attrs) > 0:
        sale_info['gift_message'] = gift_msg_attrs[0]


    non_gw = [li for li in order.line_items if li.sku != 'GW001']

    unit_sales = [_create_unitsale(us) for us in non_gw]
    tax_lines = [_create_taxlines(tl) for tl in order.tax_lines]
    return sale_info, unit_sales, tax_lines


@transaction.atomic
def _save_objects(sale, unitsales, taxlines, discount, shipping_charge, gift_wrap_fee):
    s = Sale(**sale)
    s.save()
    for u in unitsales:
        if u:
            u['sale_id'] = s.id
            u['date'] = s.sale_date
            UnitSale(**u).save()

    for tl in taxlines:
        if tl:
            tl['sale_id'] = s.id
            tl['date'] = s.sale_date
            SalesTax(**tl).save()

    adjust_amounts = Decimal('0')
    if discount != Decimal('0'):
        pa = {}
        pa['amount'] = -discount
        adjust_amounts += pa['amount']
        pa['date'] = s.sale_date
        pa['sale_id'] = s.id
        pa['adjust_type'] = 'DISCOUNT'
        ProceedsAdjustment(**pa).save()

    pa = {}
    if shipping_charge != Decimal('0'):
        pa = {}
        pa['amount'] = shipping_charge
        adjust_amounts += pa['amount']
        pa['date'] = s.sale_date
        pa['sale_id'] = s.id
        pa['adjust_type'] = 'SHIPPING_CHARGE'
        ProceedsAdjustment(**pa).save()

    if s.gift_wrapping:
        pa = {}
        pa['amount'] = gift_wrap_fee
        adjust_amounts += pa['amount']
        pa['date'] = s.sale_date
        pa['sale_id'] = s.id
        pa['adjust_type'] = 'GIFTWRAP_FEES'
        ProceedsAdjustment(**pa).save()

    pa = {}

    pa['amount'] = -shopify_fee(s, adjust_amounts)
    if pa['amount'] != Decimal('0'):
        pa['date'] = s.sale_date
        pa['sale_id'] = s.id
        pa['adjust_type'] = 'CHANNEL_FEES'
        ProceedsAdjustment(**pa).save()

    return


def load_shopify(from_date=None):
    if not from_date:
        from_date = _Shopify_start_date()

    orders = load_orders(from_date)
    orders_dict = dict((o.name, o) for o in orders)
    external_ids = orders_dict.keys()

    existing_ids = [s['external_channel_id'] for s in Sale.objects.filter(external_channel_id__in=external_ids).values('external_channel_id')]
    
    new_ids = [o for o in external_ids if o not in existing_ids]
    
    new_order_ctr = 0
    bad_order_ctr = 0
    errors = []

    for o in new_ids:
        try:    
            sale, unitsales, taxlines = _create_sale(orders_dict.get(o))
            discount = sale.pop('discount', None)
            shipping_charge = sale.pop('shipping_charge', None)
            gift_wrap_fee = sale.pop('gift_wrap_fee', None)

            _save_objects(sale, unitsales, taxlines, discount, shipping_charge, gift_wrap_fee)
            new_order_ctr += 1
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            traceback.print_exc()
            bad_order_ctr += 1
        
    summary_msg = 'Loaded Savor orders: %d new orders, %d bad orders' \
                                    % (new_order_ctr, bad_order_ctr)
    return summary_msg, errors
