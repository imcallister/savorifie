from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import *
from accountifie.common.uploaders.adaptor.model import CsvModel, TabularLayout, HeaderLayout


def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")


def channel_parse(ch):
    if ch == 'buybuy Baby':
        return 'BUYBUY'
    else:
        return 'BEDBATH'

def company_parse(c):
    if c != '':
        return 'unknown'
    else:
        return 'retail_buyer'

def parse_decimal(x):
    if x == '':
        return '0'
    else:
        return x

class BuyBuyCSVModel(CsvModel):
    external_channel_id = CharField(match="PO Number")
    shipping_charge = DecimalField(match="Shipping",
                                   transform=lambda x: parse_decimal(x.replace('$', ''))
                                   )
    sale_date = DateField(match="Order Date", transform=date_parse)
    channel_label = CharField(match="Sales Division", transform=channel_parse)
    customer_code_id = CharField(match="BillTo Company Name", transform=company_parse)
    notification_email = CharField(match="ShipTo Email")

    shipping_name = CharField(match='ShipTo Name')
    shipping_company = CharField(match='ShipTo Company Name')
    shipping_address1 = CharField(match='ShipTo Address1')
    shipping_address2 = CharField(match='ShipTo Address2')
    shipping_city = CharField(match='ShipTo City')
    shipping_zip = CharField(match='ShipTo Postal Code', transform= lambda x: x.replace("'", ""))
    shipping_province = CharField(match='ShipTo State')
    shipping_country = CharField(match='ShipTo Country')
    shipping_phone = CharField(match='BillTo Day Phone')

    quantity = IntegerField(match='Quantity')
    unit_price = DecimalField(match='Unit Cost', transform=lambda x: parse_decimal(x.replace('$', '')))
    sku = CharField(match='Vendor SKU', transform=lambda x: x.strip())

    status = CharField(match='Substatus')


    class Meta:
        delimiter = ','
        skip_rows = 5
        layout = HeaderLayout
