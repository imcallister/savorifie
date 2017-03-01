from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import *
from accountifie.common.uploaders.adaptor.model import CsvModel, TabularLayout, HeaderLayout

from inventory.models import ShippingType
from fulfill.models import Fulfillment


def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")


def tracking_parse(tr):
    if ':' in tr:
        tr = str(tr.split(':')[1])
    return tr.upper()

def parse_decimal(x):
    if x == '':
        return '0'
    else:
        return x

class FranklinCSVModel(CsvModel):
    fulfillment = DjangoModelField(Fulfillment,
                                   match="FulfillmentID",
                                   transform=lambda x: x.split('_')[0].replace('FLF', '')
                                   )
    ship_date = DateField(match="ShipDate", transform=date_parse)
    tracking_number = CharField(match="Tracking#", transform=tracking_parse)
    shipping_cost = DecimalField(match='ShippingCost', transform=parse_decimal)
    shipping_type = DjangoModelField(ShippingType,
                                     match="ShipMethod",
                                     pk='label')

    class Meta:
        delimiter = ','
        layout = HeaderLayout
