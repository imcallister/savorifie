from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import DateField, CharField, DecimalField, DjangoModelField
from accountifie.common.uploaders.adaptor.model import CsvModel, HeaderLayout

from sales.models import Sale
from accountifie.gl.models import Counterparty


def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")


def parse_sale(sid):
    return Sale.objects.filter(external_channel_id=sid).first().id

def parse_decimal(x):
    x = x.replace('$', '')
    if x == '':
        return '0'
    elif x[0] == '(':
        return '-' + x.replace('(', '').replace(')', '')
    else:
        return x


class ShopifyPayoutCSVModel(CsvModel):
    paid_thru = DjangoModelField(Counterparty, match="PaidThru")
    payout_date = DateField(match="Payout Date", transform=date_parse)
    sale = DjangoModelField(Sale, match="Order", transform=parse_sale)
    amount = DecimalField(match='Net', transform=parse_decimal)
    
    class Meta:
        delimiter = ','
        layout = HeaderLayout
