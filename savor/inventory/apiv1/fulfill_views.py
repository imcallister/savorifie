import csv
from multipledispatch import dispatch
import itertools
import logging

from django.db.models import Prefetch, Count, F

from accountifie.common.api import api_func
from inventory.models import *
from inventory.serializers import *
from base.models import *

logger = logging.getLogger('default')



def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data


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
    qs = BatchRequest.objects.all().prefetch_related('fulfillments')
    batched_flmts = [[x['id'] for x in b['fulfillments']]
                     for b in BatchRequestSerializer(qs, many=True).data]
    return list(itertools.chain(*batched_flmts))


def unbatched_fulfillments(qstring):
    batched_fulmts = batched_fulfillments(qstring)
    unbatched = Fulfillment.objects.exclude(id__in=batched_fulmts)
    fulfillments = [{'label': str(f), 'id': f.id, 'warehouse': str(f.warehouse)} for f in unbatched]
    unbatched = [f for f in fulfillments if str(f['id']) not in batched_fulmts]
    return unbatched


@dispatch(dict)
def warehousefulfill(qstring):
    qs = WarehouseFulfill.objects \
                         .all() \
                         .prefetch_related(Prefetch('fulfill_lines__inventory_item')) \
                         .select_related('warehouse', 'savor_order', 'shipping_type',
                                         'savor_transfer')

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
    qs = Fulfillment.objects \
                    .all() \
                    .prefetch_related(Prefetch('fulfill_lines')) \
                    .select_related('warehouse', 'order', 'ship_type')

    if qstring.get('warehouse'):
        qs = qs.filter(warehouse__label=qstring.get('warehouse'))

    if 'status' in qstring:
        qs = qs.filter(status__in=qstring['status'].split(','))

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
    """
    find all sale objects for which there is a fulfillment record with latest status==completed
    """
    all_sales = api_func('base', 'sale')
    all_fulfills = fulfillment(qstring)
    all_fulfill_ids = dict((str(x['order']), str(x['warehouse'])) for x in all_fulfills if x['latest_status']!='completed')

    flds = ['channel', 'id', 'order_id','items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds, warehouse):
        info = dict((k, v) for k, v in d.iteritems() if k in flds)
        info.update({'warehouse': warehouse})
        return info

    return [get_info(x, flds, all_fulfill_ids[x['label']]) for x in all_sales if x['label'] in all_fulfill_ids]


def fulfilled(qstring):
    """
    find all sale objects for which there is a fulfillment record with latest status==completed
    """
    all_sales = api_func('base', 'sale')
    all_fulfills = fulfillment({})
    all_fulfill_ids = [str(x['order']) for x in all_fulfills if x['latest_status']=='completed']

    flds = ['channel', 'id', 'order_id','items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k, v) for k, v in d.iteritems() if k in flds)

    return [get_info(x, flds) for x in all_sales if x['label'] in all_fulfill_ids]


def unfulfilled(qstring):
    """
    find all sale objects for which there is no fulfillment record
    """
    sales_qs = Sale.objects.all().prefetch_related(Prefetch('fulfillment_set'))
    unfulfilled_sales = [x for x in sales_qs if x.fulfillment_set.count()==0]

    flds = ['channel', 'id', 'items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k, v) for k, v in d.iteritems() if k in flds)

    return [get_info(x.to_json(), flds) for x in unfulfilled_sales]


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

