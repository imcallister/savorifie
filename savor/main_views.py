import sys
import traceback
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from accountifie.common.view_components import basic_modal
from accountifie.common.table import get_table
from accountifie.toolkit.utils import extractDateRange, get_company, month_tags, year_tags


# HTTP Error 500
def custom_500(request):
    type, value, tb = sys.exc_info()

    msg = '%s. %s' % (value, traceback.format_tb(tb))
    response = render(request, '500.html', {'message': msg})
    response.status_code = 200
    
    return response


@login_required
def maintenance(request):
    context = {}
    context['recent_tasks'] =  basic_modal(get_table('recent_tasks')(),
                                                      'Recent Tasks',
                                                      'recentTasks')

    return render(request, 'main_views/maintenance.html', context)


@login_required
def reports(request):
    d = {}
    d['this_month_tag'] = month_tags(0)
    d['last_month_tag'] = month_tags(-1)
    d['two_month_tag'] = month_tags(-2)

    d['this_year_ann_tag'] = year_tags(0, 'Annual')
    d['last_year_ann_tag'] = year_tags(-1, 'Annual')
    d['this_year_mthly_tag'] = year_tags(0, 'Monthly')
    d['last_year_mthly_tag'] = year_tags(-1, 'Monthly')

    return render(request, 'main_views/reports.html', d)


@login_required
def home(request):
    from_date, to_date = extractDateRange(request)
    company_id = get_company(request)
    context = dict(company_id=company_id)
    return render(request, 'main_views/home.html', context)

@login_required
def react_test(request):
    company_id = get_company(request)
    context = dict(company_id=company_id)
    return render(request, 'main_views/react_test.html', context)
