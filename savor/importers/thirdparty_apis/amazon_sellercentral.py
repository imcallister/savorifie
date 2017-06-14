import mws

from django.conf import settings

MARKETPLACE_IDs = ['ATVPDKIKX0DER', ]

ORDERS_API = mws.mws.Orders(settings.MWS_ACCESSKEY,
                            settings.MWS_SECRETKEY,
                            settings.MWS_MERCHANTID)


def _parse_order(o):
    simple_flds = ['LatestShipDate', 'FulfillmentChannel', 'PurchaseDate', 'AmazonOrderId', 'NumberOfItemsUnshipped',
                   'NumberOfItemsShipped', 'OrderStatus', 'LastUpdateDate', 'MarketplaceId', 'SalesChannel', 'BuyerEmail', 'BuyerName']

    nested_flds = ['ShippingAddress']

    order = dict((f, o.get(f, {}).get('value')) for f in simple_flds)

    for f in nested_flds:
        nested = {}
        _raw = o.get(f, {})
        order[f] = dict((nf, _raw.get(nf, {}).get('value')) for nf in _raw if nf != 'value')

    return order


def _parse_order_details(od):
    simple_flds = ['SellerSKU', 'QuantityOrdered', 'OrderItemId']

    amount_flds = ['ShippingTax', 'ShippingDiscount', 'PromotionDiscount',
                   'ItemPrice', 'ItemTax', 'ShippingPrice']

    order = dict((f, od.get(f, {}).get('value')) for f in simple_flds)
    order.update(dict((f, od.get(f, {}).get('Amount', {}).get('value')) for f in amount_flds))

    return order


def get_order(order_id):
    order = ORDERS_API.get_order([order_id]).parsed['Orders']['Order']
    return _parse_order(order)


def load_orders(created_after):
    olist = ORDERS_API.list_orders(MARKETPLACE_IDs, created_after=created_after).parsed['Orders']['Order']
    return [_parse_order(o) for o in olist]


def order_details(order_id):
    od = ORDERS_API.list_order_items(order_id).parsed['OrderItems']['OrderItem']
    if type(od) is not list:
        od = [od]

    return [_parse_order_details(d) for d in od]
