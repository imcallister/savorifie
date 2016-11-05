import itertools
from decimal import Decimal

import sales.apiv1 as sales_api
from accountifie.toolkit.utils import column_chart

def collected_salestax(qstring):
    chart_data = column_chart(title='Tax Collected',
                              y_label='Total',
                              data_labels=True)
    chart_data['plotOptions']['series']['dataLabels']['format'] = '{point.y:,.2f}'

    all_salestax = sorted(sales_api.salestax(qstring), key=lambda x: x['collector'])
    by_collector = itertools.groupby(all_salestax, lambda x: x['collector'])

    data = dict((k, sum([float(st['tax']) for st in v])) for k, v in by_collector)    
    chart_data['xAxis'] = {'categories': data.keys()}
    series_0 = {'name': 'Sales Tax Collected'}
    series_0['data'] = [float(data[k]) for k in chart_data['xAxis']['categories']]
    chart_data['series'] = [series_0]
    return chart_data
