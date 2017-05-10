import itertools
import datetime

import sales.apiv1 as sales_api
from accountifie.toolkit.utils import column_chart, line_chart, monthrange
from accountifie.query.query_manager import QueryManager
from accountifie.common.api import api_func


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


def cash_balances(qstring):
    chart_data = line_chart(title='Cash Balances',
                            y_label='Total',
                            data_labels=False)

    today = datetime.datetime.now().date()
    dt_rng = [today + datetime.timedelta(days=-x) for x in range(180)]
    dts = dict((x.isoformat(), x) for x in dt_rng if x.weekday() < 5)
    SAV_rslts = QueryManager().pd_acct_balances('SAV', dts, acct_list=['1001'])
    data = dict((x, float(SAV_rslts.loc['1001'][x])) for x in dts)

    chart_data['xAxis'] = {'categories': sorted(data.keys())}
    series_0 = {'name': 'Cash Balance'}
    series_0['data'] = [float(data[k]) for k in chart_data['xAxis']['categories']]
    chart_data['series'] = [series_0]
    return chart_data


def display_name(path):
    display_name = api_func('environment', 'alias', path)
    if display_name:
        return display_name['display_as']
    else:
        return path


def expense_trends(qstring):
    chart_data = column_chart(title='Monthly Expense Trends',
                              y_label='Total',
                              data_labels=False)

    # dynamically generate the dates
    today = datetime.datetime.now().date()
    last_year = datetime.date(today.year - 1, today.month, today.day)

    all_dts = ['%sM%02d' % (x[0], x[1]) for x in list(monthrange(last_year,
                                                                 today))]
    cols = dict(zip(all_dts, all_dts))
    raw_data = QueryManager().path_drilldown('SAV', cols, 'equity.retearnings.opexp', excl_contra=['3700'])

    # pull out top 5
    total_exp = raw_data.sum(axis=1)
    total_exp.sort()

    tbl_data = raw_data.loc[total_exp.index[:5]]
    tbl_data.loc['rest'] = raw_data.loc[total_exp.index[5:]].sum(axis=0)
    tbl_data.index = tbl_data.index.map(display_name)

    chart_data['xAxis'] = {'categories': list(tbl_data.columns)}

    def _get_series(pth):
        series = {'name': display_name(pth)}
        series['data'] = [-int(tbl_data.loc[pth, x]) for x in list(tbl_data.columns)]

        return series

    chart_data['series'] = [_get_series(pth) for pth in tbl_data.index]
    return chart_data
