import csv
from multipledispatch import dispatch
import itertools
import logging
import flatdict
import time

from django.db.models import Prefetch, Count, F

from accountifie.common.api import api_func
from inventory.models import *
from inventory.serializers import *
from base.models import *

logger = logging.getLogger('default')

def batchrequest(qstring):
    batches = BatchRequest.objects \
                          .annotate(fulfillments_count=Count('fulfillments')) \
                          .annotate(location_label=F('location__label')) \
                          .all()  \
                          .values()
    return batches


def shipmentline(qstring):
    shpmts = ShipmentLine.objects \
                         .annotate(inventory_item_label=F('inventory_item__label')) \
                         .annotate(shipment_label=F('shipment__label')) \
                         .all() \
                         .values()

    return shpmts


def batched_fulfillments(qstring):
    qs = BatchRequest.objects.all()
    qs = BatchRequestSerializer.setup_eager_loading(qs)

    batched_flmts = [[x['id'] for x in b['fulfillments']]
                     for b in BatchRequestSerializer(qs, many=True).data]
    return list(itertools.chain(*batched_flmts))


def unbatched_fulfillments(qstring):
    batches = BatchRequest.objects.all().prefetch_related('fulfillments')
    batched_flmts = list(itertools.chain(*[[x.id for x in b.fulfillments.all()] for b in batches]))
    unbatched_qs = Fulfillment.objects \
                              .select_related('warehouse') \
                              .exclude(id__in=batched_flmts)

    unb_fulfillments = [{'label': str(f), 'id': f.id, 'warehouse': str(f.warehouse)} for f in unbatched_qs]
    return unb_fulfillments


@dispatch(dict)
def warehousefulfill(qstring):
    qs = WarehouseFulfill.objects.all()

    qs = WarehouseFulfillSerializer.setup_eager_loading(qs)
    wh_flmts = WarehouseFulfillSerializer(qs, many=True).data
    for f in wh_flmts:
        f['skus'] = dict((l['inventory_item'], l['quantity']) for l in f['fulfill_lines'])
        del f['fulfill_lines']

    return wh_flmts


@dispatch(str, dict)
def warehousefulfill(warehouse_pack_id, qstring):    
    qs = WarehouseFulfill.objects \
                         .filter(warehouse_pack_id=warehouse_pack_id) \
                         .first()
    whf = WarehouseFulfillSerializer(qs).data
    whf['skus'] = dict((l['inventory_item'], l['quantity']) for l in whf['fulfill_lines'])
    del whf['fulfill_lines']

    return whf


def _missing_shipping(rec):
    if rec['ship_type'] and rec['bill_to'] != '':
            return False
    elif rec['ship_type'] == 'BY_HAND':
            return False
    else:
        return True


@dispatch(dict)
def fulfillment(qstring):
    start = time.time()
    qs = Fulfillment.objects.all()
    if qstring.get('warehouse'):
        qs = qs.filter(warehouse__label=qstring.get('warehouse'))

    if 'status' in qstring:
        qs = qs.filter(status__in=qstring['status'].split(','))
    
    qs = FulfillmentSerializer.setup_eager_loading(qs)
    flfmts = FulfillmentSerializer(qs, many=True).data
    if qstring.get('missing_shipping', '').lower() == 'true':
        flfmts = [r for r in flfmts if _missing_shipping(r)]
    for f in flfmts:
        f['skus'] = dict((l['inventory_item'], l['quantity']) for l in f['fulfill_lines'])
        del f['fulfill_lines']
    return flfmts


@dispatch(str, dict)
def fulfillment(id, qstring):
    qs = Fulfillment.objects.filter(id=id).first()
    flfmt = FulfillmentSerializer(qs).data
    flfmt['skus'] = dict((l['inventory_item'], l['quantity']) for l in flfmt['fulfill_lines'])
    del flfmt['fulfill_lines']
    return flfmt





def requested(qstring):
    unfulfilled = api_func('inventory',
                           'fulfillment',
                           qstring={'status': 'requested,partial'})

    for unf in unfulfilled:
        unf['items'] =','.join(['%s %s' % (v, k) for k,v in unf['skus'].iteritems()])
        del unf['skus']

    data = [dict((str(k), str(v)) for k, v in flatdict.FlatDict(f).iteritems()) for f in unfulfilled]
    return data


def fulfilled(qstring):
    fulfilled = api_func('inventory',
                           'fulfillment',
                           qstring={'status': 'completed'})

    for ful in fulfilled:
        ful['items'] =','.join(['%s %s' % (v, k) for k,v in ful['skus'].iteritems()])
        del ful['skus']

    data = [dict((str(k), str(v)) for k, v in flatdict.FlatDict(f).iteritems()) for f in fulfilled]
    return data


def unfulfilled(qstring):
    """
    find all sale objects for which there is no fulfillment record
    """
    fulfilled_sale_ids = [x['order_id'] for x in Fulfillment.objects.all().values('order_id')]
    sales_qs = Sale.objects.exclude(id__in=fulfilled_sale_ids) \
                           .select_related('customer_code') \
                           .select_related('channel')

    return SimpleSaleSerializer(sales_qs, many=True).data
    
    """
    sales_qs = Sale.objects.all().prefetch_related(Prefetch('fulfillment_set'))
    unfulfilled_sales = [x for x in sales_qs if x.fulfillment_set.count()==0]

    flds = ['channel', 'id', 'items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k, v) for k, v in d.iteritems() if k in flds)

    return [get_info(x.to_json(), flds) for x in unfulfilled_sales]
    """



# ????? 
def fulfill_requested(qstring):
    """
    find all sale objects for which there is a fulfillment record but no completion
    """
    update_qs = FulfillUpdate.objects.filter(status='completed') \
                                     .prefetch_related(Prefetch('fulfillment'))
    completed = [u.fulfillment.id for u in update_qs]
    incomplete = Fulfillment.objects.exclude(id__in=completed) \
                                    .select_related('order',
                                                    'warehouse', 
                                                    'ship_type',
                                                    'order__company',
                                                    'order__channel__counterparty',
                                                    'order__ship_type',
                                                    'order__customer_code')
    incomplete_sales = [f.order for f in incomplete]

    flds = ['channel', 'id', 'items_string', 'sale_date', 'shipping_name', 'shipping_company', 
            'shipping_address1', 'shipping_address2', 'shipping_city', 'shipping_province',
            'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k, v) for k, v in d.iteritems() if k in flds)

    return [get_info(x.to_json(), flds) for x in incomplete_sales]


def fulfill_request(qstring):
    """
    find all sale objects for which there is no fulfillment record
    """
    all_sales = api_func('base', 'sale')
    all_sale_ids = [x['id'] for x in all_sales]

    all_fulfills = fulfillment({})
    all_fulfill_ids = [x['id'] for x in all_fulfills]

    flds = ['channel_name', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city'
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k,v) for k,v in d.iteritems() if k in flds)

    return [get_info(x, flds) for x in all_sales if x['id'] not in all_fulfill_ids]

