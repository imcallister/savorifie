from collections import Counter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.common.table import get_table
from accountifie.common.api import api_func

@login_required
def main(request):
    user = request.user
    context = {}

    inventory_count = api_func('inventory', 'inventorycount')
    context = dict(('%s_count' % k, v) for k,v in inventory_count.iteritems())

    sales_counts = api_func('base', 'sales_counts')
    for sku in sales_counts:
        context['%s_percent_sold' % sku] = int(100.0 * float(sales_counts[sku]) / float(inventory_count[sku]))
        context['%s_sold' % sku] = sales_counts[sku]

    fulfillments = api_func('inventory', 'fulfillment')
    statuses = [x['latest_status'] for x in fulfillments]
    status_counter = dict(('%s_count' %k, v) for k,v in Counter(statuses).iteritems())
    context.update(status_counter)

    requested = [x for x in fulfillments if x['latest_status']=='requested']
    requested_warehouses = [x['warehouse'] for x in requested]
    requested_counter = dict(('%s_requested_count' %k, v) for k,v in Counter(requested_warehouses).iteritems())
    context.update(requested_counter)

    location_counts = api_func('inventory', 'locationinventory')
    context['MICH'] = sum(location_counts.get('MICH', {}).values())
    context['152Frank'] = sum(location_counts.get('152Frank', {}).values())

    channel_counts = api_func('base', 'channel_counts')
    context['shopify_total_orders'] = channel_counts.get('Shopify',0)
    context['grommet_total_orders'] = channel_counts.get('The Grommet',0)
    context['other_orders'] = sum(channel_counts.values()) - context['shopify_total_orders'] - context['grommet_total_orders']

    context['ungiftwrapped'] = len(api_func('inventory', 'ungiftwrapped'))

    context['unfulfilled_count'] = len(api_func('inventory', 'unfulfilled'))
    context['unfulfilled'] = get_table('unfulfilled')

    context['fulfill_requested_MICH'] = get_table('fulfill_requested')(warehouse='MICH')
    context['fulfill_requested_152'] = get_table('fulfill_requested')(warehouse='152Frank')
    print context['fulfill_requested_152']
    context['fulfill_confirmed'] = get_table('fulfill_confirmed')

    return render_to_response('inventory/main.html', context, context_instance = RequestContext(request))
