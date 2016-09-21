from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.common.api import api_func
from accountifie.query.query_manager import QueryManager
from accountifie.toolkit.utils import extractDateRange, get_company
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

    context['shopify_unpaid'] = get_table('unpaid_channel')('SHOPIFY')
    context['shopify_comparison'] = get_table('channel_payout_comp')('SHOPIFY')
    
    context['UPS_invoices'] = get_table('UPS_invoices')()
    context['mis_UPS'] = get_table('UPS_wrong_acct')()

    context['incomplete_expenses'] = Expense.objects.filter(account_id=unalloc_account).count()
    context['incomplete_banking'] = cashflows.filter(counterparty=None).count()
    context['incomplete_mcard'] = CreditCardTrans.objects.filter(counterparty=None).count() + \
                                  CreditCardTrans.objects.filter(counterparty_id='unknown').count()

    gl_strategy = request.GET.get('gl_strategy', None)
    query_manager = QueryManager(gl_strategy=gl_strategy)
    ap_table = query_manager.balance_by_cparty(company_id, ['3000'])
    ar_table = query_manager.balance_by_cparty(company_id, ['1100'])

    ap_rows = []
    for i in ap_table.index:
        if abs(ap_table.loc[i]) > 1:
            drilldown = '/reporting/history/account/3000/?from=%s&to=%s&cp=%s' % (from_date, to_date, i)
            ap_rows.append([i, ap_table.loc[i], drilldown])

    ar_rows = []
    for i in ar_table.index:
        if abs(ar_table.loc[i]) > 1:
            drilldown = '/reporting/history/account/1100/?from=%s&to=%s&cp=%s' % (from_date, to_date, i)
            ar_rows.append([i, ar_table.loc[i], drilldown])

    context['ap_rows'] = ap_rows
    context['ar_rows'] = ar_rows

    last_FRB = Cashflow.objects.all() \
                               .order_by('-post_date') \
                               .first() \
                               .post_date \
                               .strftime('%d-%b-%Y')

    last_CITI = CreditCardTrans.objects.all() \
                                       .order_by('-post_date') \
                                       .first() \
                                       .post_date \
                                       .strftime('%d-%b-%Y')

    last_UPS = ShippingCharge.objects \
                             .filter(shipper__company_id='UPS') \
                             .order_by('-ship_date') \
                             .first() \
                             .ship_date \
                             .strftime('%d-%b-%Y')

    last_SHOP = ChannelPayouts.objects \
                             .filter(channel__counterparty_id='SHOPIFY') \
                             .order_by('-payout_date') \
                             .first() \
                             .payout_date \
                             .strftime('%d-%b-%Y')

    context['upload_rows'] = [['Shopify Payouts', last_SHOP], ['Citicard', last_CITI],
                              ['First Republic', last_FRB], ['UPS Billing', last_UPS]]

    return render_to_response('reports/bookkeeping.html', context, context_instance = RequestContext(request))
