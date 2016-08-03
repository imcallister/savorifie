import csv
from collections import Counter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib import messages
from django.utils.safestring import mark_safe


from accountifie.common.api import api_func
from accountifie.common.models import Address
from accountifie.common.table import get_table
from accountifie.toolkit.forms import FileForm
from inventory.models import *
import inventory.importers

import datetime
import pytz

UTC = pytz.timezone('UTC')
EASTERN = pytz.timezone('US/Eastern')

def get_today():
    return datetime.datetime.utcnow().replace(tzinfo=UTC).astimezone(EASTERN).date()


def post_fulfill_update(data):
    fulfill_obj = Fulfillment.objects.get(id=data['fulfill_id'])
    fulfill_obj.status = data['status']
    fulfill_obj.save()

    FulfillUpdate(**data).save()
    return

def create_fulfill_request(warehouse, order_id):
    # check that it has not been requested already
    fulfillment_labels = [x['order'] for x in api_func('inventory', 'fulfillment')]
    warehouse_labels = [w['label'] for w in api_func('inventory', 'warehouse')]
    order = api_func('base', 'sale', unicode(order_id))
    order_label = order['label']

    if order_label in fulfillment_labels:
        return 'FULFILL_ALREADY_REQUESTED'
    elif warehouse not in warehouse_labels:
        return 'WAREHOUSE_NOT_RECOGNISED'
    else:
        # now create a fulfillment request
        today = get_today()
        warehouse = Warehouse.objects.get(label=warehouse)

        ch_ship_type = ChannelShipmentType.objects \
                                          .filter(label=order['ship_type']) \
                                          .first()

        fulfill_info = {}
        fulfill_info['request_date'] = today
        fulfill_info['warehouse_id'] = warehouse.id
        fulfill_info['order_id'] = str(order_id)
        fulfill_info['use_pdf'] = ch_ship_type.use_pdf
        fulfill_info['packing_type'] = ch_ship_type.packing_type
        fulfill_info['ship_from_id'] = ch_ship_type.ship_from.id

        if ch_ship_type:
            fulfill_info['bill_to'] = ch_ship_type.bill_to
            fulfill_info['ship_type_id'] = ch_ship_type.ship_type.id

        fulfill_info['status'] = 'requested'
        fulfill_obj = Fulfillment(**fulfill_info)
        fulfill_obj.save()

        # FIX THIS ... should be off fulfillments not sale object
        skus = api_func('base', 'sale_skus', str(order_id))
        for sku in skus:
            fline_info = {}
            fline_info['inventory_item_id'] = InventoryItem.objects.get(label=sku).id
            fline_info['quantity'] = skus[sku]
            fline_info['fulfillment_id'] = fulfill_obj.id
            fline_obj = FulfillLine(**fline_info)
            fline_obj.save()

        return 'FULFILL_REQUESTED'


@login_required
def request_fulfill(request, warehouse, order_id):
    res = create_fulfill_request(warehouse, order_id)
    if res == 'FULFILL_ALREADY_REQUESTED':
        messages.error(request, 'A fulfillment has already been requested for order %s' % order_label)
        return redirect('/admin/base/sale/?requested=unrequested')
    elif res == 'WAREHOUSE_NOT_RECOGNISED':
        messages.error(request, 'Warehouse %s not recognised for order %s' % (warehouse, order_label))
        return redirect('/admin/base/sale/?requested=unrequested')
    elif res == 'FULFILL_REQUESTED':
        messages.success(request, mark_safe('A fulfillment has been created for order %s.' % (order_label)))
        return redirect('/admin/base/sale/?requested=unrequested')
    else:
        return None


@login_required
def sales_detail(request):
    context = {}
    context['unit_sales'] = get_table('unit_sales')()

    stats = api_func('base', 'summary_sales_stats')
    context['stats'] = stats.copy()
    return render_to_response('inventory/sales_detail.html', context, context_instance = RequestContext(request))



@login_required
def thoroughbred_list(request, batch_id):
    batch = BatchRequest.objects.get(id=batch_id)
    fulfill_list = batch.fulfillments.all()
    return pick_list(request, fulfill_list.values(),
                     label='thoroughbred_batch_%s' % str(batch_id))


@login_required
def pick_list(request, data, label='shopify_pick_list'):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % label
    writer = csv.writer(response)

    inventory_names = dict((inv_item['label'], inv_item['description']) \
                           for inv_item in api_func('inventory', 'inventoryitem'))

    header_order = ['id', 'channel', 'shipping_name', 'shipping_company', 'external_routing_id',
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
    header_row += ['Ship From Company', 'Ship From Address1',
                   'Ship From Address2', 'Ship From City',
                   'Ship From ZIP'] 
    writer.writerow(header_row)

    shipping_types = dict((st['id'], st) for st in api_func('inventory', 'shippingtype'))

    hack_list = ['channel', 'shipping_name', 'shipping_company',
                 'shipping_address1', 'shipping_address2',
                 'shipping_city', 'shipping_zip', 'shipping_province',
                 'shipping_country', 'shipping_phone',
                 'notification_email', 'external_routing_id',
                 'gift_message']

    for f_req in data:
        sale_info = api_func('base', 'sale', f_req['order_id'])

        if sale_info['customer_code']!='unknown':
            for fld in hack_list:
                f_req[fld] = sale_info[fld]

            if f_req['external_routing_id'] is None:
                f_req['external_routing_id'] = ''

            if f_req['gift_message'] == '':
                f_req['gift_message'] = None

            f_req['ship_type'] = shipping_types[str(f_req['ship_type_id'])]['label']
            f_req['skus'] = api_func('base', 'sale_skus', f_req['order_id'])
            f_req['id'] = 'SAL.' + str(f_req['id'])
            f_req['shipping_zip'] = str("'" + f_req['shipping_zip'])

            line = [unicode(f_req.get(d, '')).encode('utf-8') for d in header_order]
            skus = f_req['skus'].keys()
            sku = skus[0]
            line += [sku, inventory_names[sku], f_req['skus'][sku]]

            # add the ship_from info
            ship_from = Address.objects.filter(id=f_req['ship_from_id']).first()
            if ship_from:
                line += [getattr(ship_from, fld) for fld in ['company', 'address1', 'address2',
                                                             'city', 'postal_code']]
            writer.writerow(line)

            # if more than 1 sku..
            for i in range(1, len(skus)):
                sku = skus[i]
                line = [''] * len(header_order)
                line += [sku, inventory_names[sku], f_req['skus'][sku]]
                writer.writerow(line)

            writer.writerow([unicode('=' * 20).encode('utf-8')] * (len(header_order) + 3 + 5))

    return response


@login_required
def make_batch(request, warehouse):
    warehouse_obj = Warehouse.objects.filter(label=warehouse).first()
    if not warehouse_obj:
        messages.error(request, 'No warehouse found matching %s' % warehouse)
        return redirect('/inventory/management/')
    else:
        # get all unbatched
        unbatched = api_func('inventory', 'unbatched_fulfillments')
        to_batch = [f for f in unbatched if f['warehouse'] == warehouse]

        batch_info = {}
        batch_info['created_date'] = datetime.datetime.now().date()
        batch_info['location_id'] = warehouse_obj.id
        batch = BatchRequest(**batch_info)
        batch.save()
        for f in to_batch:
            batch.fulfillments.add(f['id'])
        batch.save()

        messages.success(request, '%d fulfillments added to new batch %s' % (len(to_batch), str(batch)))
        return redirect('/inventory/management/')


@login_required
def fulfill_request(request):
    
    # 1 get unfulfilled & split into bucket
    unfulfilled = api_func('inventory', 'unfulfilled')

    shopify_no_wrap = [odr for odr in unfulfilled if odr['gift_wrapping']=='False' and odr['channel']=='Shopify']
    shopify_wrap = [odr for odr in unfulfilled if odr['gift_wrapping']!='False' and odr['channel']=='Shopify']

    # still need transfers and Grommet

    # 3 get shipping info
    # shopify no wrap shipping

    shopify_standard = api_func('inventory', 'channelshipmenttype', 'SAVOR_STANDARD')
    for odr in shopify_no_wrap:
        odr['ship_type'] = shopify_standard['ship_type']
        odr['bill_to'] = shopify_standard['bill_to']


    context = {}
    context['unit_sales'] = get_table('unit_sales')()

    stats = api_func('base', 'summary_sales_stats')
    context['stats'] = stats.copy()
    return render_to_response('inventory/sales_detail.html', context, context_instance = RequestContext(request))
