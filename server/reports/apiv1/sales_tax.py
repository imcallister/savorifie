import itertools
from decimal import Decimal

from sales.apiv1 import salestax

def collected_salestax(qstring):
    all_salestax = sorted(salestax(qstring), key=lambda x: x['collector'])
    by_collector = itertools.groupby(all_salestax, lambda x: x['collector'])

    data = dict((k, sum([Decimal(st['tax']) for st in v])) for k, v in by_collector)
    if qstring.get('chart'):
        chart_data = {}
        chart_data['x_vals'] = data.keys()
        series_0 = {'name': 'Sales Tax Collected'}
        series_0['data'] = [data[k] for k in chart_data['x_vals']]
        chart_data['series'] = [series_0]
        return chart_data
    else:
        return data
