from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import *
from accountifie.common.uploaders.adaptor.model import CsvModel, TabularLayout, HeaderLayout


def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")


def sku_parse(sk):
    if sk == 'DL-Z7RL-OS4O':
        return 'BE3'
    else:
        return sk

def flfl_channel_parse(c):
    if c == 'Amazon':
        return 'AMZN'
    else:
        return 'SAV'


def parse_gift_wrap(gw_fee):
    if gw_fee == '' or gw_fee == '0':
        return False
    else:
        return True

def parse_decimal(x):
    if x == '':
        return '0'
    else:
        return x

class AMZNOrdersCSVModel(CsvModel):
    external_channel_id = CharField(match="amazon-order-id")
    sale_date = DateField(match="purchase-date", transform=date_parse)
    

    shipping_charge = DecimalField(match="Shipping",
                                   transform=lambda x: parse_decimal(x.replace('$', ''))
                                   )
    fulfilled_by = CharField(match='fulfillment-channel', transform=flfl_channel_parse)
    quantity = IntegerField(match='quantity')
    unit_price = DecimalField(match='item-price', transform=lambda x: parse_decimal(x.replace('$', '')))
    sku = CharField(match='sku', transform=sku_parse)

    shipping_charge = DecimalField(match='shipping-price', transform=lambda x: parse_decimal(x.replace('$', '')))

    shipping_city = CharField(match='ship-city')
    shipping_zip = CharField(match='ship-postal-code')
    shipping_province = CharField(match='ship-state')
    shipping_country = CharField(match='ship-country')
    
    gift_wrap_fee = DecimalField(match='gift-wrap-price', transform=lambda x: parse_decimal(x.replace('$', '')))
    
    status = CharField(match='item-status')


    class Meta:
        delimiter = '\t'
        layout = HeaderLayout
