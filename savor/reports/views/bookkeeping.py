from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import RequestContext

from accountifie.common.api import api_func
from accountifie.common.view_components import basic_modal, bstrap_table
from accountifie.query.query_manager import QueryManager
from accountifie.toolkit.utils import extractDateRange, get_company, get_modal
from accountifie.toolkit.forms import FileForm
from accountifie.common.table import get_table
from accountifie.gl.models import ExternalAccount

from base.models import Expense, Cashflow, CreditCardTrans
from fulfill.models import ShippingCharge
from sales.models import ChannelPayouts


@login_required
def bookkeeping(request):
    company_id = get_company(request)
    from_date, to_date = extractDateRange(request)

    context = {'upload_form': FileForm()}

    unalloc_account = api_func('environment', 'variable', 'UNALLOCATED_ACCT')
    chk_acct = ExternalAccount.objects.get(gl_account__id='1001')
    cashflows = Cashflow.objects.filter(ext_account=chk_acct)
    
    context['incomplete_expenses'] = Expense.objects.filter(account_id=unalloc_account).count()
    context['incomplete_banking'] = cashflows.filter(counterparty=None).count()
    context['incomplete_mcard'] = CreditCardTrans.objects.filter(counterparty=None).count() + \
                                  CreditCardTrans.objects.filter(counterparty_id='unknown').count()

    
    return render(request, 'reports/bookkeeping.html', context)
