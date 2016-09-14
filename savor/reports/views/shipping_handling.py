from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.common.api import api_func
from accountifie.common.table import get_table
from accountifie.query.query_manager import QueryManager
from accountifie.toolkit.utils import extractDateRange, get_company
from accountifie.toolkit.forms import FileForm
from accountifie.gl.models import ExternalAccount
from base.models import Expense, Cashflow, CreditCardTrans


@login_required
def ship_charges(request):
    from_date, to_date = extractDateRange(request)

    context = {'upload_form': FileForm()}
    context['UPS_invoices'] = get_table('UPS_invoices')

    return render_to_response('reports/ship_charges.html',
                              context,
                              context_instance=RequestContext(request))
