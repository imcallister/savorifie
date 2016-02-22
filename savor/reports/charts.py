import datetime
import json
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from accountifie.query.query_manager import QueryManager
import accountifie.reporting.models
import accountifie.environment.api
from accountifie._utils import monthrange


def display_name(path):
    display_name = accountifie.environment.api.alias({'name': path})
    if display_name:
        return display_name['display_as']
    else:
        return path


@login_required
def cash_balances(request):
    today = datetime.datetime.now().date()
    dt_rng = [today + datetime.timedelta(days=-x) for x in range(180)]
    dts = dict((x.isoformat(), x) for x in dt_rng if x.weekday()<5)
    SAV_rslts = QueryManager().pd_acct_balances('SAV', dts, acct_list=['1001'])
    values = dict((x, float(-SAV_rslts.loc['1001'][x])) for x in dts)
    
    SAV_cash = SAV_rslts#.sum(axis=0).to_dict()
    
    data = {}
    data['chart_data'] = {}
    data['chart_data']['dates'] = sorted(dts)
    data['chart_data']['values'] = {'SAV': [float(SAV_cash[x]) for x in data['chart_data']['dates'] if x in SAV_cash]}
    
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def expense_trends(request):

    # dynamically generate the dates
    today = datetime.datetime.now().date()
    last_year = datetime.date(today.year-1, today.month, today.day)

    all_dts = ['%sM%02d' % (x[0], x[1]) for x in list(monthrange(last_year,today))]
    cols = dict(zip(all_dts, all_dts))
    
    raw_data = QueryManager().path_drilldown('SAV', cols, 'equity.retearnings.opexp', excl_contra=['4150'])
    # pull out top 5
    total_exp = raw_data.sum(axis=1)
    total_exp.sort()
    
    tbl_data = raw_data.loc[total_exp.index[:5]]
    tbl_data.loc['rest'] = raw_data.loc[total_exp.index[5:]].sum(axis=0)
    tbl_data.index = tbl_data.index.map(display_name)
    
    data = {}
    data['chart_data'] = {}
    data['chart_data']['dates'] = list(tbl_data.columns)
    data['chart_data']['values'] = dict((pth, [-int(tbl_data.loc[pth, x]) for x in data['chart_data']['dates']]) for pth in tbl_data.index)

    return HttpResponse(json.dumps(data), content_type='application/json')

