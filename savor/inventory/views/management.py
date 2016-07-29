from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe

from accountifie.common.api import api_func
from accountifie.common.table import get_table
from accountifie.toolkit.forms import FileForm
import base.models

@login_required
def management(request):
    context = {'shopify_upload_form': FileForm()}

    context['incomplete_shopify'] = base.models.Sale.objects.filter(customer_code='unknown').count()
    context['to_be_queued'] = len(api_func('inventory', 'unfulfilled'))
    context['unbatched_fulfillments'] = len(api_func('inventory', 'unbatched_fulfillments'))

    context['unreconciled_count'] = len([x for x in api_func('inventory', 'fulfillment') if x['status']=='requested'])

    context['missing_shipping'] = len(api_func('inventory', 'fulfillment', qstring={'missing_shipping': 'true'}))
    context['batch_columns'] = ['id', 'created_date', 'comment', 'location_label', 'fulfillments_count', 'get_list']
    batch_requests = api_func('inventory', 'batchrequest')
    for batch in batch_requests:
        link = mark_safe('<a href="/inventory/thoroughbred_list/%s/">Download</a>' % batch['id'])
        batch.update({'get_list': link})
    context['batch_rows'] = batch_requests

    thoroughbred_mismatches = api_func('inventory', 'thoroughbred_mismatch')
    context['thoroughbred_mismatches'] = len(thoroughbred_mismatches)
    context['unreconciled'] = get_table('fulfill_requested')()

    context['whmismatch_columns'] = ['order_id', 'fail_reason']
    context['whmismatch_rows'] = thoroughbred_mismatches

    return render_to_response('inventory/management.html', context, context_instance = RequestContext(request))
