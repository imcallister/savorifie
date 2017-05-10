import operator

from accountifie.toolkit.utils import column_chart
import sales.apiv1 as sales_api
import inventory.apiv1 as inventory_api


COLORS = {'BE1': '#8E4585',
          'BE2': '#229CE4',
          'BE3': '#778899',
          'SYE1': '#8E4585',
          'SYE2': '#229CE4',
          'SYE3': '#778899',
          }


def sale_count(qstring):
    chart_data = column_chart(title='Unit Sales',
                              y_label='Total',
                              data_labels=True,
                              colored_cols=True)

    item_count = sales_api.sale_count({})
    inventory_count = inventory_api.inventorycount({})

    sorted_data = sorted(item_count.items(), key=operator.itemgetter(1))
    x_labels = [x[0] for x in sorted_data]

    chart_data['xAxis'] = {'categories': x_labels}
    series_0 = {'name': 'Unit Sales (LHS)'}
    series_0['data'] = [x[1] for x in sorted_data]
    series_0['colors'] = [COLORS.get(lbl) for lbl in x_labels]

    series_1 = {'name': 'Units Ordered (RHS)'}
    series_1['data'] = [inventory_count.get(lbl) for lbl in x_labels]
    series_1['colors'] = ['black'] * len(x_labels)

    chart_data['series'] = [series_0, series_1]
    return chart_data
