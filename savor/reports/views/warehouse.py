import time
from dateutil.parser import parse

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import RequestContext
from django.utils.safestring import mark_safe

from accountifie.common.api import api_func
from accountifie.common.table import get_table
from accountifie.toolkit.forms import FileForm



@login_required
def warehouse_rec(request):
    context = {'shopify_upload_form': FileForm()}
    context['NC2_unreconciled'] = get_table('no_warehouse_record')(warehouse='NC2')
    context['152Frank_unreconciled'] = get_table('no_warehouse_record')(warehouse='152Frank')

    unrecd = api_func('fulfill', 'no_warehouse_record', {})
    context['NC2_unreconciled_count'] = len([x for x in unrecd
                                             if x['warehouse'] == 'NC2'])
    context['152Frank_unreconciled_count'] = len([x for x in unrecd
                                                  if x['warehouse'] == '152Frank'])
    
    return render(request, 'fulfillment/warehouse-rec.html', context)
