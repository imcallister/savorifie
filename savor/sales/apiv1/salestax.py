import datetime
from dateutil.parser import parse

from django.conf import settings

from ..models import Sale, SalesTax
from sales.serializers import SalesTaxSerializer, SalesTaxSerializer2



def salestax(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())
    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()
    qs = SalesTax.objects.filter(sale__sale_date__gte=start_date,
                                 sale__sale_date__lte=end_date)

    serializer = SalesTaxSerializer
    qs = serializer.setup_eager_loading(qs)
    return list(serializer(qs, many=True).data)

def salestax2(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())
    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()
    qs = Sale.objects.filter(sale_date__gte=start_date,
                             sale_date__lte=end_date)

    serializer = SalesTaxSerializer2
    qs = serializer.setup_eager_loading(qs)
    return list(serializer(qs, many=True).data)
