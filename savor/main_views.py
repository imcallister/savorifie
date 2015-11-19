import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from financifie.gl.models import ExternalBalance, ExternalAccount
from financifie.query.query_manager import QueryManager
import financifie._utils
import financifie.environment.api

from base.models import Expense, Mcard, Cashflow


@login_required
def maintenance(request):
    return render_to_response('main_views/maintenance.html', RequestContext(request, {}))

@login_required
def reports(request):
    d = {}
    return render_to_response('main_views/reports.html', RequestContext(request, d))


@login_required
def home(request):
    from_date, to_date = financifie._utils.extractDateRange(request)
    company_id = financifie._utils.get_company(request)
    #gather some info on what we have in the database
    expenses = Expense.objects.filter(company_id=company_id)
    stub_expenses = Expense.objects.filter(stub=True).count()

    chk_acct = ExternalAccount.objects.get(gl_account__id='1001')
    cashflows = Cashflow.objects.filter(ext_account=chk_acct)
    incomplete_cashflows = cashflows.filter(counterparty=None).count()

    incomplete_rows = []
    incomplete_rows.append(['Expenses', stub_expenses, '/admin/base/expense/?unmatched=UNMATCHED'])
    incomplete_rows.append(['Payments -- 1001', incomplete_cashflows, '/admin/base/cashflow/?unmatched=UNMATCHED'])



    expense_count = expenses.count()
    if expense_count:
        expense_latest = expenses.order_by('-expense_date')[0].expense_date #one sql query I hope
    else:
        expense_latest = datetime.date.today()

    

    mcard = Mcard.objects.filter(company_id=company_id)
    mcard_count = mcard.count()
    if mcard_count:
        mcard_latest = mcard.order_by('-trans_date')[0].trans_date
    else:
        mcard_latest = datetime.date.today()

    gl_strategy = request.GET.get('gl_strategy', None)
    query_manager = QueryManager(gl_strategy=gl_strategy)
    ap_table = query_manager.balance_by_cparty(company_id, ['3000'])

    ap_rows = []
    for i in ap_table.index:
        if abs(ap_table.loc[i]) > 1:
            drilldown = '/reporting/history/account/3000/?from=%s&to=%s&cp=%s' % (from_date, to_date, i)
            ap_rows.append([i, ap_table.loc[i], drilldown])


    context = dict(
        expense_count = expense_count,
        incomplete_rows = incomplete_rows,
        mcard_count = mcard_count,
        mcard_latest = mcard_latest,
        company_id = company_id,
        creditor_rows = ap_rows
        )

    return render_to_response('main_views/home.html', context, RequestContext(request))

@login_required
def daily(request):
    today = datetime.datetime.now().date()
    bank_accts = financifie.environment.api.variable_list({'name': 'BANK_ACCOUNTS'})
  
    missing_bank_bals = []

    for acct in bank_accts:
        if ExternalBalance.objects.filter(account=acct).filter(date=today).count() == 0:
            missing_bank_bals.append(acct)

    company_id = financifie._utils.get_company(request)
    from_date, to_date = financifie._utils.extractDateRange(request)
    
    # new style
    gl_strategy = request.GET.get('gl_strategy', None)

    query_manager = QueryManager(gl_strategy=gl_strategy)
    ap_table = query_manager.balance_by_cparty(company_id, ['3000'])
    prepaid_table = query_manager.balance_by_cparty(company_id, ['1250','1251'], to_date=today)
    al_table = query_manager.balance_by_cparty(company_id, ['3110'], to_date=today)

    ap_rows = []
    for i in ap_table.index:
        if abs(ap_table.loc[i]) > 1:
            drilldown = '/reporting/history/account/3000/?from=%s&to=%s&cp=%s' % (from_date, to_date, i)
            ap_rows.append([i, ap_table.loc[i], drilldown])

    prepaid_rows = []
    for i in prepaid_table.index:
        if abs(prepaid_table.loc[i]) > 1:
            drilldown = '/reporting/history/account/1250/?from=%s&to=%s&cp=%s' % (from_date, to_date, i)
            prepaid_rows.append([i, prepaid_table.loc[i], drilldown])

    al_rows = []
    for i in al_table.index:
        if abs(al_table.loc[i]) > 1:
            drilldown = '/reporting/history/account/3110/?from=%s&to=%s&cp=%s' % (from_date, to_date, i)
            al_rows.append([i, al_table.loc[i], drilldown])

    #gather some info on what we have in the database
    expenses = Expense.objects.filter(company_id=company_id)
    expense_count = expenses.count()
    if expense_count:
        expense_latest = expenses.order_by('-expense_date')[0].expense_date #one sql query I hope
    else:
        expense_latest = datetime.date.today()

    

    mcard = Mcard.objects.filter(company_id=company_id)
    mcard_count = mcard.count()
    if mcard_count:
        mcard_latest = mcard.order_by('-trans_date')[0].trans_date
    else:
        mcard_latest = datetime.date.today()

    
    if len(missing_bank_bals) > 0:
        messages.info(request, 'Missing external account balances: %s' % ','.join(missing_bank_bals))

    context = dict(
        expense_count = expense_count,
        expense_latest = expense_latest,
        mcard_count = mcard_count,
        mcard_latest = mcard_latest,
        creditor_rows = ap_rows,
        prepaid_rows = prepaid_rows,
        al_rows = al_rows,
        )


    return render_to_response('main_views/daily.html', RequestContext(request, context))

