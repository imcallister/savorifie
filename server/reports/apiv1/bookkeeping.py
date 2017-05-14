import datetime
from dateutil.parser import parse

import accountifie.query.apiv1 as query_api
from accountifie.common.api import api_func
from base.models import Expense, Cashflow, CreditCardTrans
from accountifie.gl.models import ExternalAccount

from fulfill.models import ShippingCharge
from sales.models import Payout


def receivables(qstring):
    if qstring.get('as_of'):
        as_of = parse(qstring.get('as_of')).date()
    else:
        as_of = datetime.datetime.now().date()
    rcvbles = query_api.cp_balances('SAV', {'account': '1100', 'date': as_of})

    ar_rows = []
    for rcv in rcvbles:
        cp = rcv['cp']
        amount = rcv['total']
        drill_url = '/reporting/history/account/1100/?cp=%s&to=%s' % (cp, as_of.isoformat())
        ar_rows.append({'counterparty': cp, 'amount': {'link': drill_url, 'text': amount}})
    return sorted(ar_rows, key=lambda x: float(x['amount']['text']), reverse=True)


def future_receivables(qstring):
    today = datetime.datetime.now().date()
    rcvbles = query_api.cp_balances('SAV', {'account': '1101', 'date': today})

    ar_rows = []
    for rcv in rcvbles:
        cp = rcv['cp']
        amount = rcv['total']
        drill_url = '/reporting/history/account/1101/?cp=%s&to=%s' % (cp, today.isoformat())
        ar_rows.append({'counterparty': cp, 'amount': {'link': drill_url, 'text': amount}})
    return sorted(ar_rows, key=lambda x: float(x['amount']['text']), reverse=True)


def payables(qstring):
    if qstring.get('as_of'):
        as_of = parse(qstring.get('as_of')).date()
    else:
        as_of = datetime.datetime.now().date()
    pbles = query_api.cp_balances('SAV', {'account': '3000', 'date': as_of})

    ap_rows = []
    for pbl in pbles:
        cp = pbl['cp']
        amount = pbl['total']
        drill_url = '/reporting/history/account/3000/?cp=%s&to=%s' % (cp, as_of.isoformat())
        ap_rows.append({'counterparty': cp, 'amount': {'link': drill_url, 'text': amount}})
    return sorted(ap_rows, key=lambda x: float(x['amount']['text']), reverse=True)


def last_uploads(qstring):
    output = []
    FRB = Cashflow.objects.all() \
                          .order_by('-post_date') \
                          .first() \
                          .post_date
    output.append({'Upload': 'First Republic', 'Last Upload': FRB})
    
    citi = CreditCardTrans.objects.all() \
                                  .order_by('-post_date') \
                                  .first() \
                                  .post_date
    output.append({'Upload': 'Citi Credit Card', 'Last Upload': citi})

    UPS = ShippingCharge.objects.filter(shipper__company_id='UPS') \
                                .order_by('-ship_date') \
                                .first() \
                                .ship_date
    output.append({'Upload': 'UPS', 'Last Upload': UPS})

    shopify = Payout.objects.filter(channel__counterparty_id='SHOPIFY') \
                            .order_by('-payout_date') \
                            .first() \
                            .payout_date
    output.append({'Upload': 'Shopify Payouts', 'Last Upload': shopify})
    return output


def incompletes(qstring):
    unalloc_account = api_func('environment', 'variable', 'UNALLOCATED_ACCT')
    chk_acct = ExternalAccount.objects.get(gl_account__id='1001')
    cashflows = Cashflow.objects.filter(ext_account=chk_acct)

    output = []
    output.append({'label': 'Expenses', 'fld': 'expenses', 'amount': Expense.objects.filter(account_id=unalloc_account).count()})
    output.append({'label': 'Banking', 'fld': 'banking', 'amount': cashflows.filter(counterparty=None).count()})
    mcard_cnt = CreditCardTrans.objects.filter(counterparty=None).count() + \
                CreditCardTrans.objects.filter(counterparty_id='unknown').count()
    output.append({'label': 'Mastercard', 'fld': 'mastercard', 'amount': mcard_cnt})
    
    return output
