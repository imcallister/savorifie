import csv
import flatdict
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.utils.safestring import mark_safe


from accountifie.common.models import Address
from inventory.models import Warehouse, ShippingType
from fulfill.models import BatchRequest, Fulfillment, FulfillLine, FulfillUpdate
import fulfill.serializers as flfslz
import inventory.apiv1 as inventory_api
import fulfill.apiv1 as fulfill_api
import products.apiv1 as products_api
import sales.apiv1 as sales_api

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
    warehouses = [w['label'] for w in inventory_api.warehouse({})]
    new_requests = dict((w,0) for w in warehouses)
    back_to_queue = dict((w,0) for w in warehouses)

    bad_requests = []

    if request.method == 'POST':
        for k,v in request.POST.iteritems():
            if k[:8] == 'q_choice' and v != '----':
                if v == 'Future Order':
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
                elif v[:19] == 'Queue future order for':
                    wh = v[20:]
                    rslt = backorder_to_requested(wh, k[9:])
                    if rslt == 'BACKORDER_REQUESTED':
                        back_to_queue[wh] += 1
                    else:
                        bad_requests.append(k[9:])

        msg = '%d new future orders.' % new_back_orders
        for wh in warehouses:
            msg += ' %d new %s fulfillments.' % (new_requests[wh], wh)
        for wh in warehouses:
            msg += ' %d future orders to %s.' % (back_to_queue[wh], wh)
        msg += ' %d Bad requests' % len(bad_requests)
        messages.info(request, msg)
        
        return HttpResponseRedirect("/inventory/management")
    else:
        raise ValueError("This resource requires a POST request")


@login_required
def shipping(request):
    ship_options = dict((o['label'], o) for o in inventory_api.shipoption({}))
    new_ship_choices = 0

    bad_requests = []

    if request.method == 'POST':
        for k, v in request.POST.iteritems():
            if k[:8] == 'q_choice' and v != '----':
                if v not in ship_options:
                    bad_requests.append(k)
                else:
                    flmnt = Fulfillment.objects.get(id=k.split('_')[-1])

                    flmnt.packing_type = ship_options[v]['packing_type']
                    flmnt.use_pdf = ship_options[v]['use_pdf']
                    flmnt.bill_to = ship_options[v]['bill_to']
                    flmnt.ship_from = Address.objects \
                                             .filter(label=ship_options[v]['ship_from']) \
                                             .first()

                    flmnt.ship_type = ShippingType.objects \
                                                  .filter(label=ship_options[v]['ship_type']) \
                                                  .first()

                    flmnt.save()
                    new_ship_choices += 1

        msg = '%d new ship choices.' % new_ship_choices
        msg += ' %d Bad requests' % len(bad_requests)
        messages.info(request, msg)
        return HttpResponseRedirect("/inventory/management")
    else:
        raise ValueError("This resource requires a POST request")

def create_backorder(order_id):
    # check that it has not been requested already
    unfulfilled_items = fulfill_api.unfulfilled(str(order_id), {})['unfulfilled_items']
    inv_items = dict((i['label'], i['id']) for i in products_api.inventoryitem({}))
    order = sales_api.sale(order_id, {})
    
    if unfulfilled_items is None:
        return 'FULFILL_ALREADY_REQUESTED'
    else:
        # now create a fulfillment request
        today = get_today()

        fulfill_info = {}
        fulfill_info['request_date'] = today
        fulfill_info['order_id'] = str(order_id)
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
    warehouse_labels = [w['label'] for w in inventory_api.warehouse({})]
    unfulfilled_items = fulfill_api.unfulfilled(str(order_id), {})['unfulfilled_items']
    inv_items = dict((i['label'], i['id']) for i in products_api.inventoryitem())
    order = sales_api.sale(order_id, {})

    if unfulfilled_items is None:
        return 'FULFILL_ALREADY_REQUESTED'
    elif warehouse not in warehouse_labels:
        return 'WAREHOUSE_NOT_RECOGNISED'
    elif order['ship_type'] == 'GROMWHOLE_FREIGHT':
        return 'FREIGHT_ORDER'
    else:
        # now create a fulfillment request
        today = get_today()
        warehouse = Warehouse.objects.get(label=warehouse)

        fulfill_info = {}
        fulfill_info['request_date'] = today
        fulfill_info['warehouse_id'] = warehouse.id
        fulfill_info['order_id'] = str(order_id)
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
        return redirect('/admin/sales/sale/?requested=unrequested')
    elif res == 'WAREHOUSE_NOT_RECOGNISED':
        messages.error(request, 'Warehouse %s not recognised for order %s' % (warehouse, order_label))
        return redirect('/admin/sales/sale/?requested=unrequested')
    elif res == 'FREIGHT_ORDER':
        messages.error(request, 'Order %s is for freight shipping -- ask Ian' % (warehouse, order_label))
        return redirect('/admin/sales/sale/?requested=unrequested')
    elif res == 'FULFILL_REQUESTED':
        messages.success(request, mark_safe('A fulfillment has been created for order %s.' % (order_label)))
        return redirect('/admin/sales/sale/?requested=unrequested')
    else:
        return None


@login_required
def batch_list(request, batch_id):
    batch_qs = BatchRequest.objects.get(id=batch_id)
    batch_info = flfslz.BatchRequestSerializer(batch_qs).data

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
            opt_skus.append({'inventory_item': 'MST' + inv_item,
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

    sku_names = dict((i['label'], i['description']) for i in products_api.inventoryitem({}))
    master_sku_names = dict(('MST%s' % k, '%s Master' % v) for k, v in sku_names.iteritems())
    sku_names.update(master_sku_names)

    flf_data = [{'skus': d['fulfill_lines'], 'ship': get_ship_data(d)} for d in data]

    for f in flf_data:
        f['ship']['id'] = 'FLF%s' % f['ship']['id']

    headers = OrderedDict([('SAVOR ID', 'id'),
                           ('Customer Reference', 'order:external_routing_id'),
                           ('Ship Type', 'ifs_ship_type'),
                           ('Gift Message', 'order:gift_message'),
                           ('Email', 'order:notification_email'),
                           ('Shipping Phone', 'order:shipping_phone'),
                           ('Name', 'order:shipping_name'),
                           ('Shipping Company', 'order:shipping_company'),
                           ('Shipping Address1', 'order:shipping_address1'),
                           ('Shipping Address2', 'order:shipping_address2'),
                           ('Shipping City', 'order:shipping_city'),
                           ('Shipping Province', 'order:shipping_province'),
                           ('Shipping Zip', 'order:shipping_zip'),
                           ('Shipping Country', 'order:shipping_country'),
                           ])

    header_row = headers.keys()
    header_row += [u'Item', u'Item Name', u'Quantity']
    writer.writerow(header_row)

    for flf in flf_data:
        opt_skus = optimize_NC2(flf['skus'])
        for i in range(0, len(opt_skus)):
            line = [flf['ship'].get(headers[col], '') for col in headers]
            label = opt_skus[i]['inventory_item']
            line += [label, sku_names[label], opt_skus[i]['quantity']]
            writer.writerow(line)

    return response

@login_required
def MICH_pick_list(request, data, label='MICH_batch'):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % label
    writer = csv.writer(response)

    sku_names = dict((i['label'], i['description']) for i in products_api.inventoryitem({}))
    flf_data = [{'skus': d['fulfill_lines'], 'ship': flatdict.FlatDict(d)} for d in data]

    for f in flf_data:
        f['ship']['id'] = 'FLF%s' % f['ship']['id']
    
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
        unbatched = fulfill_api.unbatched_fulfillments({})
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

