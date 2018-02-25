
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accountifie.common.api import api_func

@login_required
def inventory_counts(request):
    context = {}
    inventory_count = api_func('inventory', 'inventorycount')
    context = dict(('%s_count' % k, v) for k, v in inventory_count.iteritems())

    sales_counts = api_func('sales', 'sales_counts')
    for sku in sales_counts:
        try:
            context['%s_percent_sold' % sku] = int(100.0 * float(sales_counts.get(sku, 0)) / float(inventory_count.get(sku, 0)))
            context['%s_sold' % sku] = sales_counts[sku]
        except:
            print 'Failing on', sku

    context['location_counts'] = api_func('inventory', 'locationinventory')
    print(context)
    return render(request, 'inventory.html', context)
