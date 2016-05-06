from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.common.api import api_func
from accountifie.toolkit.forms import FileForm
import base.models

@login_required
def management(request):
    context = {'shopify_upload_form': FileForm()}

    context['incomplete_shopify'] = base.models.Sale.objects.filter(customer_code='unknown').count()
    context['to_be_queued'] = len(api_func('inventory', 'unfulfilled'))
    context['thoroughbred_mismatches'] = len(api_func('inventory', 'thoroughbred_mismatch'))

    return render_to_response('inventory/management.html', context, context_instance = RequestContext(request))
