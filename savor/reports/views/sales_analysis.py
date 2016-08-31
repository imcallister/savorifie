from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required


@login_required
def sales_analysis(request):
    context = {}
    return render_to_response('reports/sales_analysis.html', RequestContext(request, context))
