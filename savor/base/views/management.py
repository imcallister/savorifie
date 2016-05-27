from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe

from accountifie.common.api import api_func
from accountifie.common.table import get_table
from accountifie.toolkit.forms import FileForm
from accountifie.gl.models import ExternalBalance, ExternalAccount
from base.models import Expense, Cashflow, Sale, CreditCardTrans



@login_required
def management(request):
    context = {'upload_form': FileForm()}

    unalloc_account = api_func('environment', 'variable', 'UNALLOCATED_ACCT')
    chk_acct = ExternalAccount.objects.get(gl_account__id='1001')
    cashflows = Cashflow.objects.filter(ext_account=chk_acct)

    context['incomplete_expenses'] = Expense.objects.filter(account_id=unalloc_account).count()
    context['incomplete_banking'] = cashflows.filter(counterparty=None).count()
    context['incomplete_mcard'] = CreditCardTrans.objects.filter(counterparty=None).count()

    return render_to_response('base/management.html', context, context_instance = RequestContext(request))
