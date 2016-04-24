from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.common.api import api_func
from accountifie.common.table import get_table

@login_required
def main(request):
    user = request.user
    context = {}

    inventory_count = api_func('inventory', 'inventorycount')
    context = dict(('%s_count' % k, v) for k,v in inventory_count.iteritems())

    sales_counts = api_func('base', 'sales_counts')
    for sku in sales_counts:
        context['%s_sold' % sku] = int(100.0 * float(sales_counts[sku]) / float(inventory_count[sku]))
    return render_to_response('inventory/main.html', context, context_instance = RequestContext(request))

@login_required
def sales_detail(request):
    context = {}
    context['unit_sales'] = get_table('unit_sales')()

    stats = api_func('base', 'summary_sales_stats')
    context['stats'] = stats.copy()
    return render_to_response('inventory/sales_detail.html', context, context_instance = RequestContext(request))
