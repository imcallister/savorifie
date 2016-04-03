from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.common.table import get_table

@login_required
def main(request):
    user = request.user
    context = {}
    return render_to_response('inventory/main.html', context, context_instance = RequestContext(request))

@login_required
def sales_detail(request):
    context = {}
    context['unit_sales'] = get_table('unit_sales')()
    return render_to_response('inventory/sales_detail.html', context, context_instance = RequestContext(request))