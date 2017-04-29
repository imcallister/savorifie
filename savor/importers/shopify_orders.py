import os
import sys
import traceback
from dateutil.parser import parse
from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages

from .thirdparty_apis.shopify_api import load_orders
import sales.apiv1 as sales_api
from sales.models import Sale, UnitSale
from accountifie.common.api import api_func

import logging
logger = logging.getLogger('default')


PAID_THRU = {
    'Shopify Payments': 'SHOPIFY',
    'PayPal Express Checkout': 'PAYPAL',
    'Amazon Payments': 'AMZN_PMTS'
}


def upload(request):
    summary_msg, error_msgs = load_shopify()
    return JsonResponse({'summary': summary_msg, 'errors': error_msgs})

def _Shopify_start_date():
    return sales_api.sales_loaded_thru('SHOPIFY', {}).isoformat()



def _create_unitsale(us):
    try:
        sku_id = api_func('products', 'product', us.sku)['id']
        return {'quantity': int(us.quantity, '0'),
                'unit_price': Decimal(us.price),
                'sku_id': sku_id}
    except:
        return


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
    sale_info['shipping_address1'] = order.shipping_address.address1
    sale_info['shipping_address2'] = order.shipping_address.address2
    sale_info['shipping_city'] = order.shipping_address.city
    sale_info['shipping_zip'] = order.shipping_address.zip
    sale_info['shipping_province'] = order.shipping_address.province_code
    sale_info['shipping_country'] = order.shipping_address.country
    sale_info['sale_date'] = parse(order.created_at).date()
    sale_info['channel_id'] = api_func('sales', 'channel', 'SHOPIFY')['id']
    sale_info['customer_code_id'] = 'retail_buyer'
    unit_sales = [_create_unitsale(us) for us in order.line_items]
    tax_lines = [_get_taxlines(tl) for tl in order.tax_lines]
    return sale_info, unit_sales, tax_lines


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

    print 'laoded shopify orders', len(orders)
    
    for o in new_ids:
        print 'starting on', o
        
        sale, unitsales, taxlines = _create_sale(orders_dict.get(o))

        try:
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

            new_order_ctr += 1
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            traceback.print_exc()
            bad_order_ctr += 1
        print 'done with', o
    
    summary_msg = 'Loaded Savor orders: %d new orders, %d bad orders' \
                                    % (new_order_ctr, bad_order_ctr)
    return summary_msg, errors
