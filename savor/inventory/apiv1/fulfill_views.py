import csv
from multipledispatch import dispatch

from accountifie.common.api import api_func
from inventory.models import *

def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data


@dispatch(dict)
def fulfillment(qstring):
    flds = ['id', 'request_date', 'warehouse', 'order', 'order_id', 'ship_type', 'bill_to', 'latest_status']
    return [get_model_data(f, flds) for f in Fulfillment.objects.all()]


def requested(qstring):
    """
    find all sale objects for which there is a fulfillment record with latest status==completed
    """
    all_sales = api_func('base', 'sale')
    all_fulfills = fulfillment({})
    all_fulfill_ids = [str(x['order']) for x in all_fulfills if x['latest_status']!='completed']

    flds = ['channel', 'id', 'items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
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

    flds = ['channel', 'id', 'items_string', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
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

