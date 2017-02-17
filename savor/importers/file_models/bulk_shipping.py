from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import *
from accountifie.common.uploaders.adaptor.model import CsvModel, TabularLayout, HeaderLayout

from inventory.models import ShippingType, Shipper
from fulfill.models import Fulfillment


def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")


def tracking_parse(tr):
    tr = str(tr.split(':')[1])
    return tr.upper()

def shipper_parse(sh):
    return Shipper.objects.filter(company__id=sh).first().id

def parse_decimal(x):
    if x == '':
        return '0'
    else:
        return x

def boolean_parse(b):
    if (str(b).lower() == 'true'):
        return 'True'
    else:
        return 'False'

def parse_fulfillment(fl):
    try:
        return fl.split('_')[0].replace('FLF', '')
    except:
        return None


class BulkShippingCSVModel(CsvModel):
    shipper = DjangoModelField(Shipper, match='Shipper', transform=shipper_parse)
    external_id = CharField(match="External ID", transform=tracking_parse)
    tracking_number = CharField(match="Tracking#", transform=tracking_parse)
    ship_date = DateField(match="ShipDate", transform=date_parse)
    charge = DecimalField(match='Charge', transform=parse_decimal)
    invoice_number = CharField(match="Invoice#")
    fulfillment = DjangoModelField(Fulfillment,
                                   match="FulfillmentID",
                                   transform=parse_fulfillment
                                   )
    order_related = BooleanField(match="OrderRelated", transform=boolean_parse)
    
    class Meta:
        delimiter = ','
        layout = HeaderLayout
