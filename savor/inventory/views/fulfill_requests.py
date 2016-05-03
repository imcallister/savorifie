import csv
from collections import Counter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib import messages
from django.utils.safestring import mark_safe


from accountifie.common.api import api_func
from accountifie.common.table import get_table
from accountifie.toolkit.forms import FileForm
from inventory.models import Fulfillment, FulfillLine, Warehouse, ChannelShipmentType, InventoryItem, FulfillUpdate
import inventory.importers

import datetime
import pytz

UTC = pytz.timezone('UTC')
EASTERN = pytz.timezone('US/Eastern')

def get_today():
    return datetime.datetime.utcnow().replace(tzinfo=UTC).astimezone(EASTERN).date()


def post_fulfill_update(data):
    FulfillUpdate(**data).save()
    return

@login_required
def request_fulfill(request, order_id):
    # check that it has not been requested already
    fulfillment_labels = [x['order'] for x in api_func('inventory', 'fulfillment')]
    order_label = api_func('base', 'sale', unicode(order_id))['label']

    if order_label in fulfillment_labels:
        messages.error(request, 'A fulfillment has already been requested for order %s' % order_label)
        return redirect('/admin/base/sale/?requested=unrequested')
    else:
        # now create a fulfillment request
        today = get_today()
        warehouse = Warehouse.objects.get(label='MICH')
        ship_type_id = ChannelShipmentType.objects.get(label='SHOP_STANDARD').ship_type.id
        shopify_standard = api_func('inventory', 'channelshipmenttype', 'SHOP_STANDARD')

        fulfill_info = {}
        fulfill_info['request_date'] = today
        fulfill_info['warehouse_id'] = warehouse.id
        fulfill_info['order_id'] = str(order_id)
        fulfill_info['bill_to'] = shopify_standard['bill_to']
        fulfill_info['ship_type_id'] = ship_type_id
        fulfill_obj = Fulfillment(**fulfill_info)
        fulfill_obj.save()

        skus = api_func('base', 'sale_skus', str(order_id))
        for sku in skus:
            fline_info = {}
            fline_info['inventory_item_id'] = InventoryItem.objects.get(label=sku).id
            fline_info['quantity'] = skus[sku]
            fline_info['fulfillment_id'] = fulfill_obj.id
            fline_obj = FulfillLine(**fline_info)
            fline_obj.save()

        url = '/admin/inventory/fulfillment/%s/' % fulfill_obj.id
        msg = 'A fulfillment has been created for order %s. View <a href=%s>here</a>' % (order_label, url)
        messages.success(request, mark_safe(msg))
        return redirect('/admin/base/sale/?requested=unrequested')



@login_required
def sales_detail(request):
    context = {}
    context['unit_sales'] = get_table('unit_sales')()

    stats = api_func('base', 'summary_sales_stats')
    context['stats'] = stats.copy()
    return render_to_response('inventory/sales_detail.html', context, context_instance = RequestContext(request))


def _shopify_pick_info(pick_requests):
    shopify_standard = api_func('inventory', 'channelshipmenttype', 'SHOP_STANDARD')
    for odr in pick_requests:
        odr['ship_type'] = shopify_standard['ship_type']
        odr['bill_to'] = shopify_standard['bill_to']
        odr['use_pdf'] = shopify_standard['use_pdf']
        odr['packing_type'] = shopify_standard['packing_type']
        odr['skus'] = api_func('base', 'sale_skus', odr['id'])
    return pick_requests



@login_required
def shopify_pick_list(request, data):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shopify_no_wrap.csv"'
    writer = csv.writer(response)

    #data = api_func('inventory', 'shopify_no_wrap_request')
    # want to create fill requests for each
    shopify_standard = api_func('inventory', 'channelshipmenttype', 'SHOP_STANDARD')
    inventory_names = dict((inv_item['label'], inv_item['description']) for inv_item in api_func('inventory', 'inventoryitem'))

    header_order = ['id', 'channel', 'shipping_name','shipping_company', 'external_routing_id',
                    'shipping_address1', 'shipping_address2',
                    'shipping_city', 'shipping_zip', 'shipping_province',
                    'shipping_country', 'shipping_phone',
                    'notification_email', 'ship_type',
                    'bill_to', 'gift_message', 'use_pdf', 'packing_type']


    headers = {'id': 'SAVOR ID', 'channel': 'Channel', 'shipping_company': 'Shipping Company',
                'shipping_address1': 'Shipping Address1', 'shipping_address2': 'Shipping Address2',
                'shipping_city': 'Shipping City', 'shipping_zip': 'Shipping Zip', 'shipping_province': 'Shipping Province',
                'shipping_country': 'Shipping Country', 'shipping_phone': 'Shipping Phone',
                'notification_email': 'Email', 'shipping_company': 'Shipping Company', 'ship_type': 'Shipping Type',
                'bill_to': 'Bill To', 'gift_message': 'Gift Message', 'skus:sku': 'Lineitem sku',
                'skus:name': 'Lineitem name', 'skus:quantity': 'Lineitem quantity', 'external_routing_id': 'Customer Reference',
                'shipping_name': 'Name', 'use_pdf': 'Use PDF?', 'packing_type': 'Picking Slip Location'}

    header_row = [unicode(headers[x]).encode('utf-8') for x in header_order]
    header_row += [u'Item', u'Item Name', u'Quantity']
    writer.writerow(header_row)

    today = get_today()
    warehouse = Warehouse.objects.get(label='MICH')
    ship_type_id = ChannelShipmentType.objects.get(label='SHOP_STANDARD').ship_type.id

    hack_list = ['channel', 'shipping_name', 'shipping_company',
                 'shipping_address1', 'shipping_address2',
                 'shipping_city', 'shipping_zip', 'shipping_province',
                 'shipping_country', 'shipping_phone',
                 'notification_email', 'external_routing_id',
                 'gift_message']

    for f_req in data:
        sale_info = api_func('base', 'sale', f_req['order_id'])

        if sale_info['gift_wrapping'] == 'False' and sale_info['channel']=='Shopify' and sale_info['customer_code']!='unknown':
            for fld in hack_list:
                f_req[fld] = sale_info[fld]

            if f_req['external_routing_id'] is None:
                f_req['external_routing_id'] = ''

            if f_req['gift_message'] == '':
                f_req['gift_message'] = None

            f_req['ship_type'] = shopify_standard['ship_type']
            f_req['bill_to'] = shopify_standard['bill_to']
            f_req['use_pdf'] = shopify_standard['use_pdf']
            f_req['packing_type'] = shopify_standard['packing_type']
            f_req['skus'] = api_func('base', 'sale_skus', f_req['order_id'])
            f_req['id'] = 'SAL.' + str(f_req['id'])
            f_req['shipping_zip'] = str("'" + f_req['shipping_zip'])

            line = [unicode(f_req.get(d, '')).encode('utf-8') for d in header_order]
            skus = f_req['skus'].keys()
            sku = skus[0]
            line += [sku, inventory_names[sku], f_req['skus'][sku]]
            writer.writerow(line)

            # if more than 1 sku..
            for i in range(1, len(skus)):
                sku = skus[i]
                line = [''] * len(header_order)
                line += [sku, inventory_names[sku], f_req['skus'][sku]]
                writer.writerow(line)

            writer.writerow([unicode('=' * 20).encode('utf-8')] * (len(header_order) + 3))

    return response





@login_required
def fulfill_request(request):
    
    # 1 get unfulfilled & split into bucket
    unfulfilled = api_func('inventory', 'unfulfilled')

    shopify_no_wrap = [odr for odr in unfulfilled if odr['gift_wrapping']=='False' and odr['channel']=='Shopify']
    shopify_wrap = [odr for odr in unfulfilled if odr['gift_wrapping']!='False' and odr['channel']=='Shopify']

    # still need transfers and Grommet

    # 3 get shipping info
    # shopify no wrap shipping

    shopify_standard = api_func('inventory', 'channelshipmenttype', 'SHOP_STANDARD')
    for odr in shopify_no_wrap:
        odr['ship_type'] = shopify_standard['ship_type']
        odr['bill_to'] = shopify_standard['bill_to']


    context = {}
    context['unit_sales'] = get_table('unit_sales')()

    stats = api_func('base', 'summary_sales_stats')
    context['stats'] = stats.copy()
    return render_to_response('inventory/sales_detail.html', context, context_instance = RequestContext(request))
