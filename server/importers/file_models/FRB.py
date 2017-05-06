from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import *
from accountifie.common.uploaders.adaptor.model import CsvModel, HeaderLayout



def date_parse(dt):
    return parse(dt).date().strftime("%d/%m/%Y")

def parse_decimal(x):
    if x == '':
    	return '0'
    else:
    	return x


class FRBCSVModel(CsvModel):
    post_date = DateField(match="Date", transform=date_parse)
    debit = DecimalField(match="Amount Debit", transform=parse_decimal)
    credit = DecimalField(match="Amount Credit", transform=parse_decimal)
    description = CharField(match="Description")
    external_id = CharField(match="Transaction Number")


    class Meta:
        delimiter = ','
        skip_rows = 3
        layout = HeaderLayout
