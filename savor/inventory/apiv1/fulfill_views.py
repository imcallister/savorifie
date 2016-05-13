import csv
from multipledispatch import dispatch
import itertools

from accountifie.common.api import api_func
from inventory.models import *

def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data


def batchrequest(qstring):
    batches = BatchRequest.objects.all()
    flds = ['id', 'created_date', 'location', 'comment', 'fulfillment_count']
    return [get_model_data(obj, flds) for obj in batches]



def batched_fulfillments(qstring):
    batches = BatchRequest.objects.all()
    fulfillments = [[str(f) for f in b.fulfillments.all()] for b in batches]
    return [f for flist in fulfillments for f in flist]


def unbatched_fulfillments(qstring):
    fulfillments = [{'label': str(f), 'id': f.id, 'warehouse': str(f.warehouse)} for f in Fulfillment.objects.all()]
    batched_fulmts = batched_fulfillments(qstring)
    unbatched = [f for f in fulfillments if f['label'] not in batched_fulmts]
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
    wf_objs = WarehouseFulfill.objects.all()

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
            'shipping_phone', 'ship_email', 'shipping_type', 'shipping_type_label', 'tracking_number']

    obj = WarehouseFulfill.objects.get(warehouse_pack_id=warehouse_pack_id)
    obj_data = get_model_data(obj, flds)
    lines = obj.warehousefulfillline_set.all()
    obj_data['skus'] = {}
    for l in lines:
        obj_data['skus'][str(l.inventory_item)] = l.quantity

    return obj_data


@dispatch(dict)
def fulfillment(qstring):
    flds = ['id', 'request_date', 'warehouse', 'order', 'order_id', 'ship_type',
             'bill_to', 'latest_status', 'ship_info']
    
    if qstring.get('warehouse'):
        fulfill_objs = Fulfillment.objects.filter(warehouse__label=qstring.get('warehouse'))
    else:    
        fulfill_objs = Fulfillment.objects.all()
    
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
    all_fulfill_ids = [str(x['order']) for x in all_fulfills if x['latest_status']!='completed']

    flds = ['channel', 'id', 'order_id','items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k, v) for k, v in d.iteritems() if k in flds)

    return [get_info(x, flds) for x in all_sales if x['label'] in all_fulfill_ids]


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
    all_sales = api_func('base', 'sale')
    all_fulfills = fulfillment({})
    all_fulfill_ids = [str(x['order']) for x in all_fulfills]

    flds = ['channel', 'id', 'items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k, v) for k, v in d.iteritems() if k in flds)

    return [get_info(x, flds) for x in all_sales if x['label'] not in all_fulfill_ids]


def fulfill_requested(qstring):
    """
    find all sale objects for which there is a fulfillment record but no completion
    """
    all_sales = api_func('base', 'sale')
    all_sale_ids = [x['id'] for x in all_sales]

    all_fulfills = fulfillment({})
    all_fulfill_ids = [str(x['order_id']) for x in all_fulfills]

    flds = ['channel', 'id', 'items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k, v) for k, v in d.iteritems() if k in flds)

    return [get_info(x, flds) for x in all_sales if str(x['id']) not in all_fulfill_ids]


def shopify_no_wrap_request(qstring):
    unfulfilled = api_func('inventory', 'unfulfilled')
    shopify_no_wrap = [odr for odr in unfulfilled if odr['gift_wrapping'] == 'False' and odr['channel']=='Shopify' and odr['customer_code']!='unknown']
    shopify_standard = api_func('inventory', 'channelshipmenttype', 'SHOP_STANDARD')
    for odr in shopify_no_wrap:
        odr['ship_type'] = shopify_standard['ship_type']
        odr['bill_to'] = shopify_standard['bill_to']
        odr['use_pdf'] = shopify_standard['use_pdf']
        odr['packing_type'] = shopify_standard['packing_type']
        odr['skus'] = api_func('base', 'sale_skus', odr['id'])

    return shopify_no_wrap


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

