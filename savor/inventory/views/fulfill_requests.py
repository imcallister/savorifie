import csv
import flatdict
from collections import OrderedDict
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.utils.safestring import mark_safe


from accountifie.common.api import api_func
from accountifie.common.models import Address
from accountifie.common.table import get_table
from accountifie.toolkit.forms import FileForm
from inventory.models import *
import inventory.importers
import inventory.serializers as slz

import datetime
import pytz

UTC = pytz.timezone('UTC')
EASTERN = pytz.timezone('US/Eastern')

def get_today():
    return datetime.datetime.utcnow().replace(tzinfo=UTC).astimezone(EASTERN).date()


def post_fulfill_update(data):
    fulfill_obj = Fulfillment.objects.get(id=data['fulfillment_id'])
    fulfill_obj.status = data['status']
    fulfill_obj.save()

    FulfillUpdate(**data).save()
    return


@login_required
def queue_orders(request):
    new_back_orders = 0
    new_152 = 0
    new_MICH = 0

    bad_requests = []

    if request.method == 'POST':
        for k,v in request.POST.iteritems():
            if k[:8] == 'q_choice' and v != '----':
                if v == 'Back Order':
                    rslt = create_backorder(k[9:])
                    if rslt == 'FULFILL_BACKORDERED':
                        new_back_orders += 1
                    else:
                        bad_requests.append(k[9:])
                elif v == 'Queue for 152':
                    rslt = create_fulfill_request('152Frank', k[9:])
                    if rslt == 'FULFILL_REQUESTED':
                        new_152 += 1
                    else:
                        bad_requests.append(k[9:])
                elif v == 'Queue for MICH':
                    rslt = create_fulfill_request('MICH', k[9:])
                    if rslt == 'FULFILL_REQUESTED':
                        new_MICH += 1
                    else:
                        bad_requests.append(k[9:])
                    
        messages.info(request, "%d new back orders. \
                                %d new 152 fulfillments. \
                                %d new MICH fulfillments, \
                                Bad requests: %s" \
                                % (new_back_orders,
                                   new_152,
                                   new_MICH,
                                   ','.join(bad_requests)))

        return HttpResponseRedirect("/inventory/management")
    else:
        raise ValueError("This resource requires a POST request")


def create_backorder(order_id):
    # check that it has not been requested already
    fulfillment_labels = [x['order'] for x in api_func('inventory', 'fulfillment')]
    order = api_func('base', 'sale', unicode(order_id))
    order_label = order['label']

    if order_label in fulfillment_labels:
        return 'FULFILL_ALREADY_REQUESTED'
    else:
        # now create a fulfillment request
        today = get_today()
        ch_ship_type = ChannelShipmentType.objects \
                                          .filter(label=order['ship_type']) \
                                          .first()

        fulfill_info = {}
        fulfill_info['request_date'] = today
        fulfill_info['order_id'] = str(order_id)
        
        if ch_ship_type:
            fulfill_info['bill_to'] = ch_ship_type.bill_to
            fulfill_info['ship_type_id'] = ch_ship_type.ship_type.id
            fulfill_info['use_pdf'] = ch_ship_type.use_pdf
            fulfill_info['packing_type'] = ch_ship_type.packing_type
            fulfill_info['ship_from_id'] = ch_ship_type.ship_from.id


        fulfill_info['status'] = 'back-ordered'
        fulfill_obj = Fulfillment(**fulfill_info)
        fulfill_obj.save()

        unit_sales = api_func('base', 'sale', str(order_id)).get('unit_sale', [])
        u_qty = {}
        for u in unit_sales:
            for k, v in UnitSale.objects \
                                .get(id=u['id']) \
                                .inventory_items() \
                                .iteritems():
                if k in u_qty:
                    u_qty[k] += int(v)
                else:
                    u_qty[k] = int(v)

        for k,v in u_qty.iteritems():
            fline_info = {}
            fline_info['inventory_item_id'] = k
            fline_info['quantity'] = v
            fline_info['fulfillment_id'] = fulfill_obj.id
            fline_obj = FulfillLine(**fline_info)
            fline_obj.save()
        return 'FULFILL_BACKORDERED'


def backorder_to_requested(warehouse, fulfill_id):
    pass


def create_fulfill_request(warehouse, order_id):
    unfulfilled = api_func('inventory', 'unfulfilled', order_id)['unfulfilled_items']
    warehouse_labels = [w['label'] for w in api_func('inventory', 'warehouse')]

    order = api_func('base', 'sale', order_id)
    if unfulfilled is None:
        return 'FULFILL_ALREADY_REQUESTED'
    elif warehouse not in warehouse_labels:
        return 'WAREHOUSE_NOT_RECOGNISED'
    elif order['ship_type'] == 'GROMWHOLE_FREIGHT':
        return 'FREIGHT_ORDER'
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

        if ch_ship_type:
            fulfill_info['bill_to'] = ch_ship_type.bill_to
            fulfill_info['ship_type_id'] = ch_ship_type.ship_type.id
            fulfill_info['use_pdf'] = ch_ship_type.use_pdf
            fulfill_info['packing_type'] = ch_ship_type.packing_type
            fulfill_info['ship_from_id'] = ch_ship_type.ship_from.id

        fulfill_info['status'] = 'requested'
        fulfill_obj = Fulfillment(**fulfill_info)
        fulfill_obj.save()

        unfulfilled_items = api_func('inventory', 'unfulfilled', str(order_id))['unfulfilled_items']
        inv_items = dict((i['label'], i['id']) for i in api_func('inventory', 'inventoryitem'))

        for label, quantity in unfulfilled_items.iteritems():
            inv_id = inv_items[label]
            fline_info = {}
            fline_info['inventory_item_id'] = inv_id
            fline_info['quantity'] = quantity
            fline_info['fulfillment_id'] = fulfill_obj.id
            fline_obj = FulfillLine(**fline_info)
            fline_obj.save()

        return 'FULFILL_REQUESTED'


@login_required
def request_fulfill(request, warehouse, order_id):
    if request.GET.has_key('backorder'):
        if lower(request.GET.get('backorder')) == 'true':
            res = backorder_to_requested(warehouse, order_id)
        else:
            res = create_fulfill_request(warehouse, order_id)
    else:
        res = create_fulfill_request(warehouse, order_id)

    if res == 'FULFILL_ALREADY_REQUESTED':
        messages.error(request, 'A fulfillment has already been requested for order %s' % order_label)
        return redirect('/admin/base/sale/?requested=unrequested')
    elif res == 'WAREHOUSE_NOT_RECOGNISED':
        messages.error(request, 'Warehouse %s not recognised for order %s' % (warehouse, order_label))
        return redirect('/admin/base/sale/?requested=unrequested')
    elif res == 'FREIGHT_ORDER':
        messages.error(request, 'Order %s is for freight shipping -- ask Ian' % (warehouse, order_label))
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
    batch_qs = BatchRequest.objects.filter(id=batch_id)
    fulfill_list = [f['fulfillments'] for f in batch_qs.values('fulfillments')]
    fulfill_qs = Fulfillment.objects.filter(id__in=fulfill_list)
    return pick_list(request,
                     slz.FulfillmentSerializer(fulfill_qs, many=True).data,
                     label='thoroughbred_batch_%s' % str(batch_id))


@login_required
def pick_list(request, data, label='shopify_pick_list'):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % label
    writer = csv.writer(response)

    flf_data = [{'skus': d['fulfill_lines'], 'ship': flatdict.FlatDict(d)} for d in data]

    headers = OrderedDict([('SAVOR ID', 'id'),
                            ('Channel', 'order:channel'),
                            ('Name', 'order:shipping_name'),
                            ('Shipping Company', 'order:shipping_company'),
                            ('Customer Reference', 'order:external_routing_id'),
                            ('Shipping Address1', 'order:shipping_address1'),
                            ('Shipping Address2', 'order:shipping_address2'),
                            ('Shipping City', 'order:shipping_city'),
                            ('Shipping Zip', 'order:shipping_zip'),
                            ('Shipping Province', 'order:shipping_province'),
                            ('Shipping Country', 'order:shipping_country'),
                            ('Shipping Phone', 'order:shipping_phone'),
                            ('Email', 'order:notification_email'),
                            ('Shipping Type', 'ship_type'),
                            ('Bill To', 'bill_to'),
                            ('Gift Message', 'order:gift_message'),
                            ('Use PDF?', 'use_pdf'),
                            ('Pack Type', 'packing_type'),
                            ('Ship From Company', 'ship_from:company'),
                            ('Ship From Address1', 'ship_from:address1'),
                            ('Ship From Address2', 'ship_from:address2'),
                            ('Ship From City', 'ship_from:city'),
                            ('Ship From ZIP', 'ship_from:postal_code')
                           ])

    header_row = headers.keys()
    header_row += [u'Item', u'Item Name', u'Quantity']
    writer.writerow(header_row)

    for flf in flf_data:
        row = [flf['ship'].get(headers[col], '') for col in headers]
        row += [flf['skus'][0]['inventory_item'], '', flf['skus'][0]['quantity']]
        writer.writerow(row)

        # if more than 1 sku..
        for i in range(1, len(flf['skus'])):
            line = [''] * len(headers)
            line += [flf['skus'][i]['inventory_item'], '', flf['skus'][i]['quantity']]
            writer.writerow(line)

        writer.writerow([unicode('=' * 20).encode('utf-8')] * (len(header_row)))

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
