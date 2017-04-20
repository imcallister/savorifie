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


def load_orders(created_after):
	olist = ORDERS_API.list_orders(MARKETPLACE_IDs, created_after=created_after).parsed['Orders']['Order']
	return [_parse_order(o) for o in olist]

def order_details(order_id):
	return ORDERS_API.list_order_items(order_id).parsed['OrderItems']['OrderItem']
	
