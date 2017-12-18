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

def parse_tran_num(x):
    return x[:19]

class FRBCSVModel(CsvModel):
    post_date = DateField(match="Date", transform=date_parse)
    debit = DecimalField(match="Debit", transform=parse_decimal)
    credit = DecimalField(match="Credit", transform=parse_decimal)
    description = CharField(match="Statement Description")
    external_id = CharField(match="Transaction Number", transform=parse_tran_num)


    class Meta:
        delimiter = ','
        layout = HeaderLayout
