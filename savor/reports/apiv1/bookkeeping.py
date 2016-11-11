import datetime

from django.utils.safestring import mark_safe

from accountifie.query.query_manager import QueryManager
from base.models import Cashflow, CreditCardTrans
from fulfill.models import ShippingCharge
from sales.models import ChannelPayouts


def receivables(qstring):
    today = datetime.datetime.now().date()
    query_manager = QueryManager()
    ar_table = query_manager.balance_by_cparty('SAV', ['1100'], to_date=today)

    ar_rows = []
    for cp in ar_table.index:
        if abs(ar_table.loc[cp]) > 1:
            drill_url = '/reporting/history/account/1100/?cp=%s&to=%s' % (cp, today.isoformat())
            ar_rows.append({'counterparty': cp, 'amount': {'link': drill_url , 'text': ar_table.loc[cp]}})
    return ar_rows


def future_receivables(qstring):
    today = datetime.datetime.now().date()
    query_manager = QueryManager()
    ar_table = query_manager.balance_by_cparty('SAV', ['1101'], to_date=today)

    ar_rows = []
    for cp in ar_table.index:
        if abs(ar_table.loc[cp]) > 1:
            drill_url = '/reporting/history/account/1101/?cp=%s&to=%s' % (cp, today.isoformat())
            ar_rows.append({'counterparty': cp, 'amount': {'link': drill_url , 'text': ar_table.loc[cp]}})
    return ar_rows


def payables(qstring):
    query_manager = QueryManager()
    ap_table = query_manager.balance_by_cparty('SAV', ['3000'])

    ap_rows = []
    for cp in ap_table.index:
        if abs(ap_table.loc[cp]) > 1:
            drill_url = '/reporting/history/account/3000/?cp=%s' % cp
            ap_rows.append({'counterparty': cp, 'amount': {'link': drill_url , 'text': ap_table.loc[cp]}})
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
