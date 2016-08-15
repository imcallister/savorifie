import time
from dateutil.parser import parse

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe

from accountifie.common.api import api_func
from accountifie.common.table import get_table
from accountifie.toolkit.forms import FileForm


def post_button(order_id, back=False):
    html = '<select class="form-control" name="q_choice_%s"> \
              <option>----</option>' % order_id
    if back:
        for wh in ['MICH', '152Frank', 'NC2']:
            html += '<option>Queue backorder for %s</option>' % wh

    if not back:
        html += '<option>Back Order</option>'
        for wh in ['MICH', '152Frank', 'NC2']:
            html += '<option>Queue for %s</option>' % wh

    html += '</select>'
    return mark_safe(html)



def _get_name(o):
        n = o['shipping_name']
        if o['shipping_company'] and len(o['shipping_company']) > 0:
            n += ': %s' % o['shipping_company']
        return n


def _fulfill_list(qstring=None):
    orders = api_func('inventory', 'unfulfilled')
    columns = ["label", "Date", 'ship to', 'Items', 'Unfulfilled', 'Action']
    for o in orders:
        action_form = post_button(o['id'])
        o.update({'ship to': _get_name(o)})
        o.update({'Action': action_form})
        o.update({'Items': o['items_string']})
        o.update({'Unfulfilled': o.get('unfulfilled_string', '')})
        o.update({'Date': parse(o['sale_date']).strftime('%d-%b-%y')})
    return columns, orders


def _backorder_list(qstring=None):
    back_fulfills = api_func('inventory', 'backordered')

    columns = ["label", "Date", 'ship to', 'Items', 'Unfulfilled', 'Action']
    for f in back_fulfills:
        action_form = post_button(f['id'], back=True)

        items = [(i['inventory_item'], i['quantity']) for i in f['fulfill_lines']]
        items = sorted(items, key=lambda x: x[0])
        items_string = ','.join(['%s %s' %(i[1], i[0]) for i in items])

        o = f['order']
        f.update({'ship to': _get_name(o)})
        f.update({'Action': action_form})
        f.update({'Items': items_string})
        f.update({'Unfulfilled': items_string})
        f.update({'Date': parse(o['sale_date']).strftime('%d-%b-%y')})
    return columns, back_fulfills


@login_required
def management(request):
    start = time.time()
    context = {'shopify_upload_form': FileForm()}

    context['incomplete_orders'] = api_func('base', 'incomplete_sales_count')

    context['tbq_columns'], context['tbq_rows'] = _fulfill_list()
    context['to_be_queued'] = len(context['tbq_rows'])

    context['back_columns'], context['back_rows'] = _backorder_list()
    context['backordered'] = len(context['back_rows'])

    context['unbatched_fulfillments'] = len(api_func('inventory', 'unbatched_fulfillments'))
    context['unreconciled_count'] = len([x for x in api_func('inventory', 'fulfillment') if x['status']=='requested'])
    context['missing_shipping'] = len(api_func('inventory', 'fulfillment',
                                               qstring={'missing_shipping': 'true',
                                                        'status': 'requested'}))

    context['batch_columns'] = ['id', 'created_date', 'comment', 'location', 'fulfillment_count', 'get_list']

    batch_requests = sorted(api_func('inventory', 'batchrequest'),
                            key=lambda x: x['created_date'],
                            reverse=True)
    for batch in batch_requests:
        link = mark_safe('<a href="/inventory/batch_list/%s/">Download</a>' % batch['id'])
        batch.update({'get_list': link})
    context['batch_rows'] = batch_requests

    thoroughbred_mismatches = api_func('inventory', 'thoroughbred_mismatch')
    context['thoroughbred_mismatches'] = len(thoroughbred_mismatches)
    context['unreconciled'] = get_table('fulfill_requested')()
    context['whmismatch_columns'] = ['fulfill_id', 'fail_reason']
    context['whmismatch_rows'] = thoroughbred_mismatches

    return render_to_response('inventory/management.html', context, context_instance = RequestContext(request))
