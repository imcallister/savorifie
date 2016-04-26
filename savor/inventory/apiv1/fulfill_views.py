import csv

from accountifie.common.api import api_func
from inventory.models import *




def fulfillment(qstring):
    return list(Fulfillment.objects.all().values())


def unfulfilled(qstring):
    """
    find all sale objects for which there is no fulfillment record
    """
    all_sales = api_func('base', 'sale')
    all_sale_ids = [x['id'] for x in all_sales]

    all_fulfills = fulfillment({})
    all_fulfill_ids = [x['order_id'] for x in all_fulfills]

    flds = ['channel', 'id', 'sale_date', 'shipping_name', 'shipping_company', 'shipping_address1', 'shipping_address2', 'shipping_city',
            'shipping_province', 'shipping_zip', 'shipping_country', 'notification_email', 'shipping_phone',
            'gift_message', 'gift_wrapping', 'memo', 'customer_code', 'external_channel_id', 'external_routing_id']

    def get_info(d, flds):
        return dict((k, v) for k, v in d.iteritems() if k in flds)

    return [get_info(x, flds) for x in all_sales if x['id'] not in all_fulfill_ids]


def shopify_no_wrap_request(qstring):
    unfulfilled = api_func('inventory', 'unfulfilled')
    shopify_no_wrap = [odr for odr in unfulfilled if odr['gift_wrapping'] == 'False' and odr['channel']=='Shopify']

    shopify_standard = api_func('inventory', 'channelshipmenttype', 'SHOP_STANDARD')
    for odr in shopify_no_wrap:
        odr['ship_type'] = shopify_standard['ship_type']
        odr['bill_to'] = shopify_standard['bill_to']
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

