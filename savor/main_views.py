import sys
import traceback
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from accountifie.toolkit.utils import extractDateRange, get_company


# HTTP Error 500
def custom_500(request):
    type, value, tb = sys.exc_info()

    msg = '%s. %s' % (value, traceback.format_tb(tb))
    response = render(request, '500.html', {'message': msg})
    response.status_code = 200
    
    return response


@login_required
def maintenance(request):
    return render(request, 'main_views/maintenance.html', {})


@login_required
def reports(request):
    return render(request, 'main_views/reports.html', {})


@login_required
def home(request):
    from_date, to_date = extractDateRange(request)
    company_id = get_company(request)
    context = dict(company_id=company_id)
    return render(request, 'main_views/home.html', context)
