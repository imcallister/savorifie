from collections import Counter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.common.table import get_table
from accountifie.common.api import api_func

@login_required
def inventory_counts(request):
    user = request.user
    context = {}

    inventory_count = api_func('inventory', 'inventorycount')
    context = dict(('%s_count' % k, v) for k,v in inventory_count.iteritems())

    sales_counts = api_func('sales', 'sales_counts')
    for sku in sales_counts:
        context['%s_percent_sold' % sku] = int(100.0 * float(sales_counts[sku]) / float(inventory_count[sku]))
        context['%s_sold' % sku] = sales_counts[sku]

    context['location_counts'] = api_func('inventory', 'locationinventory')

    return render_to_response('inventory/main.html', context, context_instance = RequestContext(request))
