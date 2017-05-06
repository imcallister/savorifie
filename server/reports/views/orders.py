from dateutil.parser import parse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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
    return render(request, 'orders_list.html', context)

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
    context['special_sale'] = sku_data['special_sale']
    context['sale_comment'] = sku_data['memo']
    context['giftwrap'] = 'Yes' if sku_data['gift_wrapping'] else 'No'
    context['gift_message'] = sku_data['gift_message']

    context['fulfillment_list'] = []

    for f in fulfillments:
        batch = api_func('fulfill', 'fulfillment_batch', str(f['id']))
        batch_id = batch.get('batch_id') if batch else 'unbatched'
        fulfill_info = {'id': f['id'], 'batch_id': batch_id}
        fulfill_info['warehouse'] = f['warehouse']
        fulfill_info['request_date'] = parse(f['request_date']).strftime('%d-%b-%y')
        fulfill_info['items_requested'] = f['items_string']
        fulfill_info['status'] = f['status']
        
        ship_type = f.get('ship_type')
        if ship_type:
            fulfill_info['ship_type'] = ship_type.get('label', 'Unknown')
        else:
            fulfill_info['ship_type'] = 'Unknown'
        
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

        if f.get('warehousefulfill_count', 0) > 0:
            fulfill_info['wh_fulfill_info'] = True
            context['whFulfillInfo'] = get_modal(get_table('whouse_records')(f['id']),
                                                           'Shipping Info',
                                                           'whFulfillInfo')
        else:
            fulfill_info['wh_fulfill_info'] = False

        context['fulfillment_list'].append(fulfill_info)

    return render(request, 'order_drilldown.html', context)
