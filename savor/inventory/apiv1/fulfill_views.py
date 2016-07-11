import csv
from multipledispatch import dispatch
import itertools
import logging

from django.db.models import Prefetch

from accountifie.common.api import api_func
from inventory.models import *
from base.models import *

logger = logging.getLogger('default')

def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data


def batchrequest(qstring):
    batches = BatchRequest.objects.all() \
                                  .select_related('location') \
                                  .prefetch_related('fulfillments')
    return [batch.to_json(expand=['fulfillment_count']) for batch in batches]


def shipmentline(qstring):
    shpmts = ShipmentLine.objects.all()
    return [shpmt.to_json() for shpmt in shpmts]


def batched_fulfillments(qstring):
    qs = BatchRequest.objects.all().prefetch_related('fulfillments')
    batched_f = [[str(x.id) for x in batch.fulfillments.all()] for batch in qs]
    return list(itertools.chain(*batched_f))


def unbatched_fulfillments(qstring):
    batched_fulmts = batched_fulfillments(qstring)
    unbatched = Fulfillment.objects.exclude(id__in=batched_fulmts)
    fulfillments = [{'label': str(f), 'id': f.id, 'warehouse': str(f.warehouse)} for f in unbatched]
    unbatched = [f for f in fulfillments if str(f['id']) not in batched_fulmts]
    return unbatched


@dispatch(dict)
def warehousefulfill(qstring):
    flds = ['savor_order', 'savor_order_id', 'savor_transfer', 'warehouse',
            'warehouse_pack_id', 'order_date', 'request_date',
            'ship_date', 'shipping_name', 'shipping_attn', 'shipping_address1',
            'shipping_address2', 'shipping_address3', 'shipping_city',
            'shipping_zip', 'shipping_province', 'shipping_country',
            'shipping_phone', 'ship_email', 'shipping_type', 'shipping_type_id','tracking_number']

    data = []
    wf_objs = WarehouseFulfill.objects.all() \
                .prefetch_related(Prefetch('warehousefulfillline_set__inventory_item')) \
                .select_related('warehouse', 'savor_order', 'shipping_type',
                                'savor_transfer', 'savor_order__channel',
                                'savor_order__channel__counterparty')

    for obj in wf_objs:
        obj_data = get_model_data(obj, flds)
        lines = obj.warehousefulfillline_set.all()

        obj_data['skus'] = {}
        for l in lines:
            obj_data['skus'][str(l.inventory_item)] = l.quantity

        data.append(obj_data)

    return data


@dispatch(str, dict)
def warehousefulfill(warehouse_pack_id, qstring):
    flds = ['savor_order', 'savor_order_id', 'savor_transfer', 'warehouse',
            'warehouse_pack_id', 'order_date', 'request_date',
            'ship_date', 'shipping_name', 'shipping_attn', 'shipping_address1',
            'shipping_address2', 'shipping_address3', 'shipping_city',
            'shipping_zip', 'shipping_province', 'shipping_country',
            'shipping_phone', 'ship_email', 'shipping_type', 'shipping_type', 'tracking_number']

    obj = WarehouseFulfill.objects.get(warehouse_pack_id=warehouse_pack_id)
    obj_data = get_model_data(obj, flds)
    lines = obj.warehousefulfillline_set.all()
    obj_data['skus'] = {}
    for l in lines:
        obj_data['skus'][str(l.inventory_item)] = l.quantity

    return obj_data


@dispatch(dict)
def fulfillment2(qstring):
    flds = ['id', 'request_date', 'warehouse', 'order', 'order_id', 'ship_type',
            'bill_to', 'latest_status', 'ship_info']

    if qstring.get('warehouse'):
        fulfill_objs = Fulfillment.objects \
                        .filter(warehouse__label=qstring.get('warehouse')) \
                        .prefetch_related(Prefetch('fulfillline_set'),
                                          Prefetch('fulfillupdate_set')) \
                        .select_related('warehouse', 'order', 'ship_type')
    else:
        fulfill_objs = Fulfillment.objects \
                                  .all() \
                                  .prefetch_related(Prefetch('fulfillline_set'),
                                                    Prefetch('fulfillupdate_set')) \
                                  .select_related('warehouse', 'order', 'ship_type')

    fulfill_data = [obj.to_json(expand=['fulfilllines', 'latest_status']) for obj in fulfill_objs]

    if qstring.get('missing_shipping', '').lower() == 'true':
        fulfill_data = [x for x in fulfill_data if x.get('ship_info') == 'incomplete']

    if 'status' in qstring:
        fulfill_data = [x for x in fulfill_data if qstring['status'] in [u['status'] for u in x['updates']]]

    return fulfill_data


@dispatch(dict)
def fulfillment(qstring):
    flds = ['id', 'request_date', 'warehouse', 'order', 'order_id', 'ship_type',
             'bill_to', 'latest_status', 'ship_info']

    if qstring.get('warehouse'):
        fulfill_objs = Fulfillment.objects \
                        .filter(warehouse__label=qstring.get('warehouse')) \
                        .prefetch_related(Prefetch('fulfillline_set__inventory_item'),
                                          Prefetch('fulfillupdate_set')) \
                        .select_related('warehouse', 'order', 'ship_type', 
                                        'order__channel',
                                        'order__channel__counterparty')
    else:
        fulfill_objs = Fulfillment.objects \
                          .all() \
                          .prefetch_related(Prefetch('fulfillline_set__inventory_item'),
                                            Prefetch('fulfillupdate_set')) \
                          .select_related('warehouse', 'order', 'ship_type', 
                                        'order__channel',
                                        'order__channel__counterparty')

    if qstring.get('missing_shipping', '').lower() == 'true':
        fulfill_objs = [x for x in fulfill_objs if x.ship_info == 'incomplete']

    all_fulfill = []
    for obj in fulfill_objs:
        data = get_model_data(obj, flds)

        lines = obj.fulfillline_set.all()
        data['skus'] = {}
        for l in lines:
            data['skus'][str(l.inventory_item)] = l.quantity

        all_fulfill.append(data)

    if 'status' in qstring:
        return [req for req in all_fulfill if req['latest_status'] == qstring['status']]
    else:
        return all_fulfill


@dispatch(str, dict)
def fulfillment(id, qstring):
    flds = ['id', 'request_date', 'warehouse', 'order', 'order_id', 'ship_type',
             'bill_to', 'latest_status', 'ship_info']
    obj = Fulfillment.objects.get(id=id)
    data = get_model_data(obj, flds)

    lines = obj.fulfillline_set.all()
    data['skus'] = {}
    for l in lines:
        data['skus'][str(l.inventory_item)] = l.quantity

    return data


def ungiftwrapped(qstring):
    """
    find all sale objects with gift wraps for which there either no fulfillment record or latest status!=completed
    """
    all_sales = api_func('base', 'sale')
    all_fulfills = fulfillment({})
    completed_ids = [str(x['order']) for x in all_fulfills if x['latest_status']=='completed']

    flds = ['channel', 'id', 'order_id','items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k, v) for k, v in d.iteritems() if k in flds)

    return [get_info(x, flds) for x in all_sales if x['label'] not in completed_ids and x['gift_wrapping']=='True']


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

