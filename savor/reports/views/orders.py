from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.common.api import api_func
import tables.bstrap_tables


@login_required
def orders(request):
    context = {}
    context['title'] = 'Orders'
    context['content'] = tables.bstrap_tables.orders_list()
    return render_to_response('orders_list.html',
                              context,
                              context_instance=RequestContext(request))

@login_required
def order_drilldown(request, order_id):
    # gather info
    sale_info = api_func('sales', 'sale', order_id, qstring={'view': 'fulfillment'})
    sku_data = api_func('sales', 'sale', order_id) 

    def get_fulfillment(id):
        return api_func('fulfill', 'fulfillment', id, qstring={'view': 'full'})

    fulfillments = [get_fulfillment(id) for id in sale_info['fulfillment_ids']]

    context = {}
    context['title'] = 'Orders'
    context['label'] = sale_info['label']
    context['channel'] = sale_info['channel']
    context['items_string'] = sale_info['items_string']
    context['gift_wrapping'] = sale_info['gift_wrapping']
    context['unfulfilled'] = sale_info['unfulfilled_string']

    context['unit_sales'] = [{'quantity': u['quantity'],
                              'unit_price': u['unit_price'],
                              'sku': u['sku']} for u in sku_data['unit_sale']]

    fulfill_cols = ['request_date', 'items_string', 'status', 'warehouse', 'bill_to']
    context['fulfillment_cols'] = fulfill_cols
    update_cols = ['update_date', 'comment', 'status', 'shipper', 'tracking_number']
    context['update_cols'] = update_cols

    context['fulfillment_list'] = []

    for f in fulfillments:
        batch = api_func('fulfill', 'fulfillment_batch', str(f['id']))
        batch_id = batch.get('batch_id') if batch else 'unbatched'
        fulfill_data = {'id': f['id'], 'batch_id': batch_id}
        fulfill_data['fulfill'] = [f[col] for col in fulfill_cols]
        fulfill_data['updates'] = [[u[u_col] for u_col in update_cols] for u in f['fulfill_updates']]
        context['fulfillment_list'].append(fulfill_data)

    return render_to_response('order_drilldown.html',
                              context,
                              context_instance=RequestContext(request))
