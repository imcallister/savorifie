from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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
    context['IFS_monthly'] = get_table('IFS_monthly')

    return render(request, 'reports/ship_charges.html', context)
