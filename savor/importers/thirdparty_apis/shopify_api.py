import shopify
from dateutil.parser import parse

from django.conf import settings

SHOP_URL = "https://%s:%s@%s.myshopify.com/admin" % (settings.SHOPIFY_APIKEY, 
													 settings.SHOPIFY_PASSWORD,
													 settings.SHOPIFY_SHOPNAME)


def _load_session(f):
	shopify.ShopifyResource.set_site(SHOP_URL)
	return f
	
@_load_session
def load_order(id):
	return shopify.Order().find(id)

@_load_session
def load_orders(from_date):
	from_str = parse(from_date).strftime('%Y-%m-%d') + ' 00:00'
	orders = shopify.Order().find(created_at_min=from_str)
	return orders