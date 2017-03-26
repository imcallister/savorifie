import logging
from decimal import Decimal

from sales.models import Sale
from accountifie.gl.models import Counterparty

import accountifie.gl.apiv1 as gl_api
import accountifie.reporting.apiv1 as rptg_api


from fulfill.models import WarehouseFulfill, Fulfillment, ShippingCharge
from sales.models import Payout, PayoutLine
from base.models import NominalTransaction, NominalTranLine
from sales.importers.shopify import shopify_fee

from fulfill.calcs import create_nc2_shippingcharge

logger = logging.getLogger('default')

def add_shopify_fees():
    for s in Sale.objects.filter(channel__label='SHOPIFY'):
        s.channel_charges = shopify_fee(s)
        s.save()
    return

def fix_shopify_fees():
    # weren't getting calc'd from 15th Sep to 28th Oct
    to_fix = Sale.objects.filter(channel__label='SHOPIFY').filter(sale_date__gte='2016-09-15')
    for s in to_fix:
        s.channel_charges = shopify_fee(s)
        s.save()
    return

def backfill_shopify_payees():
    shopify = Counterparty.objects.get(id='SHOPIFY')
    for s in Sale.objects.filter(channel__label='SHOPIFY'):
        s.paid_thru = shopify
        s.save()


def backfill_nc2_shipcharges():
    # delete the old ones
    ShippingCharge.objects.filter(shipper__company__id='IFS360').delete()

    new_charges = 0
    duplicated_not_saved = 0
    unknown = 0
    for wf in WarehouseFulfill.objects \
                              .filter(warehouse__label='NC2'):
        ret_code = create_nc2_shippingcharge(wf)
        if ret_code == 'SHIPPING CHARGE ALREADY EXISTS':
            duplicated_not_saved += 1
        elif ret_code == 'SHIPPING CHARGE CREATED':
            new_charges += 1
        else:
            unknown += 1

    logger.info('Manual Migration: backfill_nc2_shipcharges')
    logger.info('%s new shipping charges, %s duplicated not saved, %s unknown' \
                % (new_charges, duplicated_not_saved, unknown))
    return

def backfill_nc2_packing_ids():
    success_ctr = 0
    error_ctr = 0
    
    for sc in ShippingCharge.objects.filter(shipper__company__id='IFS360'):
        try:
            sc.packing_id = sc.invoice_number
            sc.invoice_number = None
            sc.save()
            success_ctr += 1
        except:
            error_ctr += 1

    logger.info('Manual Migration: backfill_nc2_packing_ids')
    logger.info('%s shipping charges amended, %s errors' \
                % (success_ctr, error_ctr))
    return    

"""
def backfill_payouts():
    old_payouts = ChannelPayouts.objects.all()

    for op in old_payouts:
        np = Payout()
        np.payout = op.payout
        np.channel = op.channel
        np.payout_date = op.payout_date
        if op.paid_thru:
            np.paid_thru = op.paid_thru
        else:
            np.paid_thru = op.channel
        
        np.save()

        for s in op.sales.all():
            npl = PayoutLine()
            npl.payout = np
            npl.sale = s
            npl.amount = s.total_receivable()
            npl.save()
"""

def year_end_entries():
    bals = rptg_api.balances('SAV', {'as_of': '2016-12-31'})
    accounts = gl_api.account({})
    
    acct_paths = dict((a['id'], a['path']) for a in accounts if 'equity.retearnings.' in a['path'])
    RET_EARNINGS = [a['id'] for a in accounts if a['path'] == 'equity.retearnings'][0]

    noml = {'company_id': 'SAV',
            'date': '2017-01-01',
            'comment': 'Year end to retained earnings'}

    noml_obj = NominalTransaction(**noml)
    noml_obj.save()

    total_amount = Decimal('0')

    # now create nominal tran lines
    for a_id in acct_paths.keys():
        noml_line = {}
        noml_line['transaction'] = noml_obj
        noml_line['account_id'] = a_id
        noml_line['counterparty_id'] = 'SAV'
        amount = Decimal('%.2f' % bals.get(a_id, 0))
        total_amount += amount
        noml_line['amount'] = -amount
        NominalTranLine(**noml_line).save()

    # now save the balancing entry
    noml_line = {}
    noml_line['transaction'] = noml_obj
    noml_line['account_id'] = RET_EARNINGS
    noml_line['counterparty_id'] = 'SAV'
    noml_line['amount'] = total_amount
    NominalTranLine(**noml_line).save()

    # fprce GL entries to be sent
    noml_obj.save() 

    

