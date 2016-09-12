import itertools
from decimal import Decimal

from sales.apiv1 import salestax

def collected_salestax(qstring):
    all_salestax = sorted(salestax(qstring), key=lambda x: x['collector'])
    by_collector = itertools.groupby(all_salestax, lambda x: x['collector'])
    return dict((k, sum([Decimal(st['tax']) for st in v])) for k, v in by_collector)
