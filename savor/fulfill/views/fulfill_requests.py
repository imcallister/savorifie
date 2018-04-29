import csv
import flatdict
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.utils.safestring import mark_safe

from accountifie.common.api import api_func
from accountifie.common.models import Address
from inventory.models import Warehouse, ShippingType
from fulfill.models import BatchRequest, Fulfillment, FulfillLine
import fulfill.serializers as flfslz
from reports.calcs.unbatched_fulfillments import unbatched_fulfillments

import datetime
from dateutil.parser import parse
import pytz

UTC = pytz.timezone('UTC')
EASTERN = pytz.timezone('US/Eastern')

def get_today():
    return datetime.datetime.utcnow().replace(tzinfo=UTC).astimezone(EASTERN).date()


@login_required
def queue_orders(request):
    new_back_orders = 0
    warehouses = [w['label'] for w in api_func('inventory', 'warehouse')]
    new_requests = dict((w, 0) for w in warehouses)
    back_to_queue = dict((w, 0) for w in warehouses)

    bad_requests = []
    msg = ''

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
                elif 'Queue future order' in v:
                    wh = v[23:]
                    rslt = backorder_to_requested(wh, k[9:])
                    if rslt == 'BACKORDER_REQUESTED':
                        back_to_queue[wh] += 1
                    else:
                        bad_requests.append(k[9:])

        if new_back_orders >0 :
            msg += '%d new future orders.' % new_back_orders
        for wh in warehouses:
            if new_requests[wh] > 0:
                msg += ' %d new %s fulfillments.' % (new_requests[wh], wh)
        for wh in warehouses:
            if back_to_queue[wh] > 0:
                msg += ' %d future orders to %s.' % (back_to_queue[wh], wh)
        if len(bad_requests) > 0:
            msg += ' %d Bad requests' % len(bad_requests)
        messages.info(request, msg)
        
        return HttpResponseRedirect("/fulfillment/management")
    else:
        raise ValueError("This resource requires a POST request")


@login_required
def shipping(request):
    ship_options = dict((o['label'], o) for o in api_func('inventory', 'shipoption'))
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
        return HttpResponseRedirect("/fulfillment/management")
    else:
        raise ValueError("This resource requires a POST request")

def create_backorder(order_id):
    # check that it has not been requested already
    unfulfilled_items = api_func('sales', 'unfulfilled', str(order_id))['unfulfilled_items']
    inv_items = dict((i['label'], i['id']) for i in api_func('products', 'inventoryitem'))

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
    return 'BACKORDER_REQUESTED'


def create_fulfill_request(warehouse, order_id):
    warehouse_labels = [w['label'] for w in api_func('inventory', 'warehouse')]
    unfulfilled_items = api_func('sales', 'unfulfilled', str(order_id))['unfulfilled_items']
    inv_items = dict((i['label'], i['id']) for i in api_func('products', 'inventoryitem'))
    
    if unfulfilled_items is None:
        return 'FULFILL_ALREADY_REQUESTED'
    elif warehouse not in warehouse_labels:
        return 'WAREHOUSE_NOT_RECOGNISED'
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
        if request.GET.get('backorder').lower() == 'true':
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

    if batch_info['location'] == 'NC2':
        return NC2_pick_list(request, batch_info['fulfillments'],
                              label='NC2_batch_%s' % str(batch_id))
    elif batch_info['location'] == 'FBA':
        return FBA_batch(request, batch_info['fulfillments'],
                              label='FBA_batch_%s' % str(batch_id))



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


def _map_sku(savor_sku):
    if savor_sku == 'BE3':
        return 'DL-Z7RL-OS4O'
    else:
        return savor_sku


@login_required
def FBA_batch(request, data, label='FBA_batch'):
    constants = {'DisplayableComment': 'Here is a displayable_comment',
                 'DisplayableOrderComment': 'Thanks so much for your Savor order! If you love your keepsake box, please share it with your friends by tagging us @savor.it.all. For customer returns, please email customerserivce@savor.us',
                 'DeliverySLA': 'Standard',
                 'FulfillmentAction': 'Ship',
                 'MarketplaceID': 'ATVPDKIKX0DER',
                 'PerUnitDeclaredValue': ''}

    col_order = ['MerchantFulfillmentOrderID',  'DisplayableOrderID',  'DisplayableOrderDate', 'MerchantSKU', 'Quantity',
                 'MerchantFulfillmentOrderItemID', 'GiftMessage', 'DisplayableComment', 'PerUnitDeclaredValue',
                 'DisplayableOrderComment', 'DeliverySLA', 'AddressName', 'AddressFieldOne', 'AddressFieldTwo', 'AddressFieldThree',
                 'AddressCity', 'AddressCountryCode', 'AddressStateOrRegion', 'AddressPostalCode', 'AddressPhoneNumber',
                 'NotificationEmail', 'FulfillmentAction', 'MarketplaceID']


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % label
    writer = csv.writer(response)

    flf_data = [{'skus': d['fulfill_lines'], 'ship': flatdict.FlatDict(d)} for d in data]
    for f in flf_data:
        f['ship']['id'] = 'FLF%s' % f['ship']['id']
        f['ship']['order_date'] = datetime.datetime.now().isoformat().split('.')[0]
        f['ship']['country_code'] = 'US'

    headers = {'DisplayableOrderID': 'id',
               'DisplayableOrderDate': 'order_date',
               'MerchantFulfillmentOrderItemID': 'id',
               'GiftMessage': 'order:gift_message',
               'NotificationEmail': 'order:notification_email',
               'AddressPhoneNumber': 'order:shipping_phone',
               'AddressName': 'order:shipping_name',
               'AddressFieldThree': 'order:shipping_company',
               'AddressFieldOne': 'order:shipping_address1',
               'AddressFieldTwo': 'order:shipping_address2',
               'AddressCity': 'order:shipping_city',
               'AddressStateOrRegion': 'order:shipping_province',
               'AddressPostalCode': 'order:shipping_zip',
               'AddressCountryCode': 'country_code'}

    writer.writerow(col_order)
    for flf in flf_data:
        for i, fl in enumerate(flf['skus']):
            line = dict((col, flf['ship'].get(headers[col], '')) for col in headers)
            line = dict((k, v.encode('utf-8') if v is not None else '') for k, v in line.items)
            line['MerchantSKU'] = _map_sku(fl['inventory_item'])
            line['Quantity'] = fl['quantity']
            line['MerchantFulfillmentOrderItemID'] += str(i) 
            line.update(constants)
            writer.writerow([line.get(h) for h in col_order])

    return response


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

    sku_names = dict((i['label'], i['description']) for i in api_func('products', 'inventoryitem'))
    master_sku_names = dict(('MST%s' % k, '%s Master' % v) for k, v in sku_names.iteritems())
    sku_names.update(master_sku_names)

    flf_data = [{'skus': d['fulfill_lines'], 'ship': get_ship_data(d)} for d in data]

    for f in flf_data:
        f['ship']['id'] = 'FLF%s' % f['ship']['id']

    headers = OrderedDict([('SAVOR ID', 'id'),
                           ('CUSTOMER REFERENCE', 'order:external_routing_id'),
                           ('SHIP TYPE', 'ifs_ship_type'),
                           ('GIFT MESSAGE', 'order:gift_message'),
                           ('CUSTOMER E-MAIL', 'order:notification_email'),
                           ('SHIPPING PHONE', 'order:shipping_phone'),
                           ('NAME', 'order:shipping_name'),
                           ('SHIPPING COMPANY', 'order:shipping_company'),
                           ('SHIPPING ADDRESS 1', 'order:shipping_address1'),
                           ('SHIPPING ADDRESS 2', 'order:shipping_address2'),
                           ('SHIPPING CITY', 'order:shipping_city'),
                           ('SHIPPING PROVIENCE', 'order:shipping_province'),
                           ('SHIPPING ZIP', 'order:shipping_zip'),
                           ('SHIPPING Country', 'order:shipping_country'),
                           ])

    header_row = headers.keys()
    header_row += [u'ITEM NAME', u'ITEM QTY']
    writer.writerow(header_row)

    for flf in flf_data:
        opt_skus = optimize_NC2(flf['skus'])
        for i in range(0, len(opt_skus)):
            line = [flf['ship'].get(headers[col], '') for col in headers]
            line = [x if x is not None else '' for x in line]
            line = [x.encode('utf-8') for x in line]
            label = opt_skus[i]['inventory_item']
            line += [label, opt_skus[i]['quantity']]

            writer.writerow(line)

    return response



@login_required
def make_batch(request, warehouse):
    warehouse_obj = Warehouse.objects.filter(label=warehouse).first()
    if not warehouse_obj:
        messages.error(request, 'No warehouse found matching %s' % warehouse)
        return redirect('/fulfillment/management/')
    else:
        # get all unbatched
        unbatched = unbatched_fulfillments({})
        to_batch = [f for f in unbatched if f['warehouse'] == warehouse]

        if len(to_batch) > 0:
            batch_info = {}
            batch_info['created_date'] = datetime.datetime.now().date()
            batch_info['location_id'] = warehouse_obj.id
            batch = BatchRequest(**batch_info)
            batch.save()
            for f in to_batch:
                batch.fulfillments.add(f['id'])
            batch.save()
            messages.success(request, '%d fulfillments added to new batch %s' % (len(to_batch), str(batch)))
        else:
            messages.success(request, 'No fulfillments to be batched for %s' % (warehouse))
        return redirect('/fulfillment/management/')

