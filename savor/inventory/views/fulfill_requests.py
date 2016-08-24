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
import inventory.apiv1 as inventory_api
import base.apiv1 as base_api


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
    warehouses = [w['label'] for w in inventory_api.warehouse()]
    new_requests = dict((w,0) for w in warehouses)
    back_to_queue = dict((w,0) for w in warehouses)

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
                elif v[:9] == 'Queue for':
                    wh = v[10:]
                    rslt = create_fulfill_request(wh, k[9:])
                    if rslt == 'FULFILL_REQUESTED':
                        new_requests[wh] += 1
                    else:
                        bad_requests.append(k[9:])
                elif v[:19] == 'Queue backorder for':
                    wh = v[20:]
                    rslt = backorder_to_requested(wh, k[9:])
                    if rslt == 'BACKORDER_REQUESTED':
                        back_to_queue[wh] += 1
                    else:
                        bad_requests.append(k[9:])

        msg = '%d new back orders.' % new_back_orders
        for wh in warehouses:
            msg += ' %d new %s fulfillments.' % (new_requests[wh], wh)
        for wh in warehouses:
            msg += ' %d backorders to %s.' % (back_to_queue[wh], wh)
        msg += ' %d Bad requests' % len(bad_requests)
        messages.info(request, msg)
        
        return HttpResponseRedirect("/inventory/management")
    else:
        raise ValueError("This resource requires a POST request")


def create_backorder(order_id):
    # check that it has not been requested already
    unfulfilled = api_func('inventory', 'unfulfilled', order_id)['unfulfilled_items']
    unfulfilled_items = api_func('inventory', 'unfulfilled', str(order_id))['unfulfilled_items']
    inv_items = dict((i['label'], i['id']) for i in api_func('inventory', 'inventoryitem'))
    order = api_func('base', 'sale', order_id)
    
    if unfulfilled is None:
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

        for label, quantity in unfulfilled_items.iteritems():
            inv_id = inv_items[label]
            fline_info = {}
            fline_info['inventory_item_id'] = inv_id
            fline_info['quantity'] = quantity
            fline_info['fulfillment_id'] = fulfill_obj.id
            fline_obj = FulfillLine(**fline_info)
            fline_obj.save()

    return 'FULFILL_BACKORDERED'


def backorder_to_requested(warehouse, fulfill_id):
    fulfill_obj = Fulfillment.objects.get(id=fulfill_id)
    fulfill_obj.status = 'requested'
    fulfill_obj.warehouse = Warehouse.objects.get(label=warehouse)
    fulfill_obj.save()

    update = FulfillUpdate()
    update.update_date = get_today()
    update.comment = 'back-ordered to requested'
    update.status = 'requested'
    update.fulfillment = fulfill_obj
    update.save()
    return 'BACKORDER_REQUESTED'


def create_fulfill_request(warehouse, order_id):
    unfulfilled = api_func('inventory', 'unfulfilled', order_id)['unfulfilled_items']
    warehouse_labels = [w['label'] for w in api_func('inventory', 'warehouse')]
    unfulfilled_items = api_func('inventory', 'unfulfilled', str(order_id))['unfulfilled_items']
    inv_items = dict((i['label'], i['id']) for i in api_func('inventory', 'inventoryitem'))
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
def batch_list(request, batch_id):
    batch_qs = BatchRequest.objects.get(id=batch_id)
    batch_info = slz.BatchRequestSerializer(batch_qs).data
    
    if batch_info['location'] == 'MICH':
        return MICH_pick_list(request, batch_info['fulfillments'],
                              label='MICH_batch_%s' % str(batch_id))
    elif batch_info['location'] == 'NC2':
        return NC2_pick_list(request, batch_info['fulfillments'],
                              label='NC2_batch_%s' % str(batch_id))
    elif batch_info['location'] == '152Frank':
        return MICH_pick_list(request, batch_info['fulfillments'],
                              label='152Frank_batch_%s' % str(batch_id))
    

NC2_NOTES = {
    'UNCOMMON': 'Must use UG packing slip PDF (attached).  Must use UG shipping label (attached).  Packing slip goes in clear pouch on side of box #1.',
    'PSOURCE': 'Must affix barcode stickers from Fineline technology to back of the product on the bottom right corner. Orders > 150 pounds should be palletized and shipped fedex FREIGHT ECONOMY to warehouse 7801 Industrial Drive, Forest Park, IL 60130, Attn: Product.   We need dimensions, wt for BOL.  Savor to provide BOL (attached).  Shipper name with PO number on all boxes.  Mark 1 of 2, 2 of 2 etc.   To schedule pickup call 18663934585.',
    'BEDBATH': 'Must use bed bath packing slip PDF (attached). Must use fedex label (attached).',
    'BUYBUY': 'Must use buybuy BABY packing slip PDF (attached). Must use fedex label (attached).',
    'GROMMET': 'Must use Grommet packing slip PDF (attached).  Must use Grommet mailing label (attached).',
    'GROMWHOLE': 'Must use Grommet packing slip PDF (attached). Must use Grommet mailing label (attached)',
    'AMZN': 'Must use Amazon packing label (attached).',
    'WAYFAIR': 'Must use Wayfair packing label (attached).  Must use Wayfair mailing label (attached)',
    'SHOPIFY': ''
}


def optimize_NC2(skus):
    opt_skus = []
    for sku in skus:
        qty = sku['quantity']
        inv_item = sku['inventory_item']
        if qty < 2:
            opt_skus.append({'inventory_item': inv_item,
                             'quantity': qty})
        else:
            # make some masters
            mstr_cnt = qty // 2
            opt_skus.append({'inventory_item': 'MAS' + inv_item,
                             'quantity': mstr_cnt})

            # any left over as single
            sngl_cnt = qty - 2 * mstr_cnt
            if sngl_cnt > 0:
                opt_skus.append({'inventory_item': inv_item,
                                 'quantity': sngl_cnt})
    return opt_skus


@login_required
def NC2_pick_list(request, data, label='MICH_batch'):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % label
    writer = csv.writer(response)

    def get_ship_data(d):
        fd = flatdict.FlatDict(d)
        fd['notes'] = NC2_NOTES.get(fd['order:channel'], '')
        if fd['ship_type']['label'] == 'FREIGHT':
            fd['ifs_ship_type'] = 'PICK'
        elif fd['ship_type']['label'] == 'IFS_BEST':
            fd['ifs_ship_type'] = 'BEST'
        else:
            fd['ifs_ship_type'] = 'HOLD'
        return fd

    sku_names = dict((i['label'], i['description']) for i in api_func('inventory', 'inventoryitem'))
    master_sku_names = dict(('MAS%s' % k, '%s Master' % v) for k, v in sku_names.iteritems())
    sku_names.update(master_sku_names)

    flf_data = [{'skus': d['fulfill_lines'], 'ship': get_ship_data(d)} for d in data]

    for f in flf_data:
        f['id'] = 'FLF%s' % f

    headers = OrderedDict([('SAVOR ID', 'id'),
                            ('Channel', 'order:channel'),
                            ('Ship Type', 'ifs_ship_type'),
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
                            ('Gift Message', 'order:gift_message'),
                            ('Notes', 'notes'),
                           ])

    header_row = headers.keys()
    header_row += [u'Item', u'Item Name', u'Quantity']
    writer.writerow(header_row)

    for flf in flf_data:
        opt_skus = optimize_NC2(flf['skus'])
        row = [flf['ship'].get(headers[col], '') for col in headers]
        label = opt_skus[0]['inventory_item']
        row += [label, sku_names[label], opt_skus[0]['quantity']]
        writer.writerow(row)

        # if more than 1 sku..
        for i in range(1, len(opt_skus)):
            line = [''] * len(headers)
            label = opt_skus[i]['inventory_item']
            line += [label, sku_names[label], opt_skus[i]['quantity']]
            writer.writerow(line)

        writer.writerow([unicode('=' * 20).encode('utf-8')] * (len(header_row)))

    return response

@login_required
def MICH_pick_list(request, data, label='MICH_batch'):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % label
    writer = csv.writer(response)

    sku_names = dict((i['label'], i['description']) for i in api_func('inventory', 'inventoryitem'))
    flf_data = [{'skus': d['fulfill_lines'], 'ship': flatdict.FlatDict(d)} for d in data]

    for f in flf_data:
        f['id'] = 'FLF%s' % f
    
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
                            ('Shipping Type', 'ship_type:description'),
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
        label = flf['skus'][0]['inventory_item']
        row += [label, sku_names[label], flf['skus'][0]['quantity']]
        writer.writerow(row)

        # if more than 1 sku..
        for i in range(1, len(flf['skus'])):
            line = [''] * len(headers)
            label = flf['skus'][i]['inventory_item']
            line += [label, sku_names[label], flf['skus'][i]['quantity']]
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
