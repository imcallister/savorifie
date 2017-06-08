from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import DateField, DecimalField, DjangoModelField
from accountifie.common.uploaders.adaptor.model import CsvModel, HeaderLayout

from sales.models import Sale


def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")


def parse_sale(sid):
    s = Sale.objects.filter(checkout_id=sid).first()
    if s:
        return s.id
    else:
        return None


def parse_decimal(x):
    x = x.replace('$', '')
    if x == '':
        return '0'
    elif x[0] == '(':
        return '-' + x.replace('(', '').replace(')', '')
    else:
        return x


class AMZNPmtsPayoutCSVModel(CsvModel):
    payout_date = DateField(match="Payout Date", transform=date_parse)
    sale = DjangoModelField(Sale, match="CheckoutID", transform=parse_sale)
    amount = DecimalField(match='Amount', transform=parse_decimal)

    class Meta:
        delimiter = ','
        layout = HeaderLayout
