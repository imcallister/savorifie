import sys
import traceback
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from accountifie.common.view_components import basic_modal
from accountifie.common.table import get_table
from accountifie.toolkit.utils import get_company
from accountifie.toolkit.forms import FileForm

# HTTP Error 500
def custom_500(request):
    type, value, tb = sys.exc_info()

    msg = '%s. %s' % (value, traceback.format_tb(tb))
    response = render(request, '500.html', {'message': msg})
    response.status_code = 200
    
    return response


@login_required
def maintenance(request):
    context = {}
    context['recent_tasks'] = basic_modal(get_table('recent_tasks')(),
                                                      'Recent Tasks',
                                                      'recentTasks')

    return render(request, 'main_views/maintenance.html', context)


@login_required
def reports(request):
    return render(request, 'main_views/reports.html', {})


@login_required
def home(request):
    company_id = get_company(request)
    context = dict(company_id=company_id)
    return render(request, 'main_views/home.html', context)

@login_required
def react(request):
    return render(request, 'main_views/index.html', {})


@login_required
def load_orders(request):
    output = []
    context = {'shopify_upload_form': FileForm()}
    return render(request, 'fulfillment/load_orders.html', context)
