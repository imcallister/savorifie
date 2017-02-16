from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import *
from accountifie.common.uploaders.adaptor.model import CsvModel, TabularLayout, HeaderLayout

from inventory.models import ShippingType, Shipper
from fulfill.models import Fulfillment


def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")


def tracking_parse(tr):
    try:
        return '{0:.0f}'.format(float(tr))
    except:
        return tr.upper()

def shipper_parse(sh):
    return Shipper.objects.filter(company__id=sh).first().id

def parse_decimal(x):
    if x == '':
        return '0'
    else:
        return x

class BulkShippingCSVModel(CsvModel):
    shipper = DjangoModelField(Shipper, match='Shipper', transform=shipper_parse)
    external_id = CharField(match="External ID", transform=tracking_parse)
    tracking_number = CharField(match="Tracking#", transform=tracking_parse)
    ship_date = DateField(match="ShipDate", transform=date_parse)
    charge = DecimalField(match='Charge', transform=parse_decimal)
    invoice_number = CharField(match="Invoice#")
    fulfillment = DjangoModelField(Fulfillment,
                                   match="FulfillmentID",
                                   transform=lambda x: x.split('_')[0].replace('FLF', '')
                                   )
    order_related = BooleanField(match="ShipDate", transform=date_parse)
    
    class Meta:
        delimiter = ','
        layout = HeaderLayout
