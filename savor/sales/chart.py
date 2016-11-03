import operator
from decimal import Decimal

import sales.apiv1 as sales_api


def sale_count(qstring):
    chart_data = {
        'chart': {
            'type': 'column'
        },
        'title': {
            'text': 'Unit Sales'
        },
        'yAxis': {
            'title': {
                'text': 'Total'
            }
        },
        'plotOptions': {
          'series': {
            'dataLabels': {
              'enabled': True
            },
          }
        },
        'credits': {
            'enabled': False
        }
      }

    item_count = sales_api.sale_count({})
    sorted_data = sorted(item_count.items(), key=operator.itemgetter(1))
    chart_data['xAxis'] = {'categories': [x[0] for x in sorted_data]}
    series_0 = {'name': 'Unit Sales'}
    series_0['data'] = [x[1] for x in sorted_data]
    chart_data['series'] = [series_0]
    return chart_data
