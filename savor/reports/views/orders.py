from dateutil.parser import parse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.common.api import api_func
import fulfill.apiv1 as flfl_api
import tables.bstrap_tables
from accountifie.toolkit.utils import get_modal
from accountifie.common.table import get_table




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
    # ORDER INFO
    context['sale_label'] = sale_info['label']
    context['sale_id'] = order_id
    context['shipping_to'] = sale_info['shipping_name']
    if sale_info['shipping_company']:
        context['shipping_to'] += ' / %s' % sale_info['shipping_company']
    context['items'] = sale_info['items_string']
    context['unfulfilled_items'] = sale_info['unfulfilled_string']
    context['sale_date'] = parse(sale_info['sale_date']).strftime('%d-%b-%y')
    context['special_sale'] = "No"
    context['sale_comment'] = "Blah di blah di barca"
    context['giftwrap'] = "No"
    context['gift_message'] = "None"


    # FULFILL REQUESTS

    fulfill_cols = ['request_date', 'items_string', 'status', 'warehouse', 'bill_to']
    context['fulfillment_cols'] = fulfill_cols
    update_cols = ['update_date', 'comment', 'status', 'shipper', 'tracking_number']
    context['update_cols'] = update_cols

    context['fulfillment_list'] = []

    for f in fulfillments:
        batch = api_func('fulfill', 'fulfillment_batch', str(f['id']))
        batch_id = batch.get('batch_id') if batch else 'unbatched'
        fulfill_info = {'id': f['id'], 'batch_id': batch_id}
        fulfill_info['warehouse'] = f['warehouse']
        fulfill_info['request_date'] = parse(f['request_date']).strftime('%d-%b-%y')
        fulfill_info['items_requested'] = f['items_string']
        fulfill_info['status'] = f['status']
        fulfill_info['ship_type'] = f['ship_type']['label']
        fulfill_info['bill_to'] = f['bill_to']

        ship_charges = flfl_api.shippingcharge({'fulfill': f['id']})
        if len(ship_charges) > 0:
            fulfill_info['ship_info'] = True
            fulfill_info['num_packages'] = len(ship_charges)
            context['shipInfo'] = get_modal(get_table('shipping_info')(f['id']),
                                                      'Shipping Info',
                                                      'shipInfo')
        else:
            fulfill_info['ship_info'] = False

        context['fulfillment_list'].append(fulfill_info)

    return render_to_response('order_drilldown.html',
                              context,
                              context_instance=RequestContext(request))
