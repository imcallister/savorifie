import sys
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from accountifie.toolkit.utils import extractDateRange, get_company


# HTTP Error 500
def custom_500(request):
    type, value, tb = sys.exc_info(),

    response = render_to_response(
        '500.html',
        context_instance=RequestContext(request, {'message': value})
    )
    
    response.status_code = 200
    
    return response


@login_required
def maintenance(request):
    return render_to_response('main_views/maintenance.html', RequestContext(request, {}))


@login_required
def reports(request):
    d = {}
    return render_to_response('main_views/reports.html', RequestContext(request, d))


@login_required
def home(request):
    from_date, to_date = extractDateRange(request)
    company_id = get_company(request)
    context = dict(company_id=company_id)
    return render_to_response('main_views/home.html', context, RequestContext(request))
