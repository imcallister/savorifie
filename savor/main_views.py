from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from accountifie.toolkit.utils import extractDateRange, get_company


import tables.bstrap_tables

def custom_500(request):
    t = loader.get_template('500.html')
    type, value, tb = sys.exc_info(),
    return HttpResponseServerError(t.render(Context({
                                     'message': value,
                                    })))

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
