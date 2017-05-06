from dateutil.parser import parse

from accountifie.common.uploaders.adaptor.fields import *
from accountifie.common.uploaders.adaptor.model import CsvModel, HeaderLayout



class IFSMonthlyCSVModel(CsvModel):
    warehouse_pack_id = CharField(match="ID Reg (*)")
    invoice_id = CharField(match="Statement Number")
    
    class Meta:
        delimiter = ','
        layout = HeaderLayout
