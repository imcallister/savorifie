from models import Sale
from importers.shopify import shopify_fee

def add_shopify_fees():
    for s in Sale.objects.filter(channel__label='SHOPIFY'):
        s.channel_charges = shopify_fee(s)
        s.save()
    return

