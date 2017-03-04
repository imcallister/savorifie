from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import CharField, DateField, DecimalField
from accountifie.common.uploaders.adaptor.model import CsvModel, HeaderLayout


def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")


def tracking_parse(tr):
    try:
        return '{0:.0f}'.format(float(tr))
    except:
        return tr.upper()

def parse_decimal(x):
    if x == '':
        return '0'
    else:
        return x

class FBACSVModel(CsvModel):
    warehouse_pack_id = CharField(match="shipment-id")
    
    external_channel_id = CharField(match="amazon-order-id")
    ship_date = DateField(match="shipment-date", transform=date_parse)
    tracking_number = CharField(match="tracking-number", transform=tracking_parse)
    ship_email = CharField(match="buyer-email")

    shipping_name = CharField(match="recipient-name")
    shipping_zip = CharField(match="ship-postal-code")
    shipping_country = CharField(match="ship-country")
    shipping_charge = DecimalField(match="shipping-price",
                                   transform=lambda x: parse_decimal(x.replace('$', ''))
                                   )
    carrier = CharField(match="carrier")
    ship_level = CharField(match="ship-service-level")
    
    class Meta:
        delimiter = '\t'
        layout = HeaderLayout
