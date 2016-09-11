from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import *
from accountifie.common.uploaders.adaptor.model import CsvModel, TabularLayout, HeaderLayout

from inventory.models import ShippingType
from fulfill.models import Fulfillment


SHIP_MAP = {'FEG': 'FEDEX_GROUND', 'PMD': 'USPS_PRIORITY', 'GRND': 'UPS_GROUND',
            'FDXHD': 'FEDEX_GROUND', 'UPSGC': 'UPS_GROUND', 'LTL': 'FREIGHT',
            'UPSLTL': 'FREIGHT'}


def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")


def tracking_parse(tr):
    try:
        return '{0:.0f}'.format(float(tr))
    except:
        return tr.upper()


class NC2CSVModel(CsvModel):
    warehouse_pack_id = CharField(match="ShipNum")
    fulfillment = DjangoModelField(Fulfillment,
                                   match="OrderNum",
                                   transform=lambda x: x.split('_')[0].replace('FLF', '')
                                   )
    request_date = DateField(match="OrderDate", transform=date_parse)
    ship_date = DateField(match="ShipDate", transform=date_parse)
    shipping_name = CharField(match="Name")
    shipping_attn = CharField(match="Company")
    shipping_zip = CharField(match="Zip")
    shipping_country = CharField(match="Country")
    ship_email = CharField(match="Email")
    tracking_number = CharField(match="Tracking#", transform=tracking_parse)
    weight = DecimalField(match='Weight [Lbs.]')
    shipping_cost = DecimalField(match='ShippingCost')
    handling_cost = DecimalField(match='HandlingCost')
    shipping_type = DjangoModelField(ShippingType,
                                     match="ShipMethod",
                                     transform=lambda x: SHIP_MAP.get(x),
                                     pk='label')

    class Meta:
        delimiter = ','
        layout = HeaderLayout
