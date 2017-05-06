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


class UPSCSVModel(CsvModel):
    account = CharField(match="Account Number")
    invoice_number = CharField(match="Invoice Number")
    ship_date = DateField(match="Pickup Date", transform=date_parse)
    charge = DecimalField(match='Net Amount', transform=lambda x: x.replace(',', ''))
    tracking_number = CharField(match="Tracking Number")

    class Meta:
        delimiter = ','
        skip_rows = 6
        layout = HeaderLayout
