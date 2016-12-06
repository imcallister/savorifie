import datetime

import accountifie.query.apiv1 as query_api
from base.models import Cashflow, CreditCardTrans
from fulfill.models import ShippingCharge
from sales.models import ChannelPayouts


def receivables(qstring):
    today = datetime.datetime.now().date()
    rcvbles = query_api.cp_balances('SAV', {'account': '1100', 'date': today})

    ar_rows = []
    for rcv in rcvbles:
        cp = rcv['cp']
        amount = rcv['total']
        drill_url = '/reporting/history/account/1100/?cp=%s&to=%s' % (cp, today.isoformat())
        ar_rows.append({'counterparty': cp, 'amount': {'link': drill_url, 'text': amount}})
    return ar_rows


def future_receivables(qstring):
    today = datetime.datetime.now().date()
    rcvbles = query_api.cp_balances('SAV', {'account': '1101', 'date': today})

    ar_rows = []
    for rcv in rcvbles:
        cp = rcv['cp']
        amount = rcv['total']
        drill_url = '/reporting/history/account/1101/?cp=%s&to=%s' % (cp, today.isoformat())
        ar_rows.append({'counterparty': cp, 'amount': {'link': drill_url, 'text': amount}})
    return ar_rows


def payables(qstring):
    today = datetime.datetime.now().date()
    pbles = query_api.cp_balances('SAV', {'account': '3000', 'date': today})

    ap_rows = []
    for pbl in pbles:
        cp = pbl['cp']
        amount = pbl['total']
        drill_url = '/reporting/history/account/3000/?cp=%s&to=%s' % (cp, today.isoformat())
        ap_rows.append({'counterparty': cp, 'amount': {'link': drill_url, 'text': amount}})
    return ap_rows


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

    shopify = ChannelPayouts.objects.filter(channel__counterparty_id='SHOPIFY') \
                                    .order_by('-payout_date') \
                                    .first() \
                                    .payout_date
    output.append({'Upload': 'Shopify Payouts', 'Last Upload': shopify})

    return output
