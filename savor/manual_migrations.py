import logging
from decimal import Decimal, ROUND_HALF_UP

from sales.models import Sale
from accountifie.gl.models import Counterparty

import accountifie.gl.apiv1 as gl_api
import accountifie.reporting.apiv1 as rptg_api
from accountifie.query.query_manager_strategy_factory import QueryManagerStrategyFactory


from savor.base.models import NominalTransaction, NominalTranLine
from fulfill.models import WarehouseFulfill, ShippingCharge, Fulfillment, FulfillLine
from sales.models import UnitSale, SalesTax, ProceedsAdjustment
from sales.importers.shopify import shopify_fee
import inventory.apiv1 as inventory_api
import products.apiv1 as products_api
import fulfill.apiv1 as fulfill_api
from fulfill.calcs import create_nc2_shippingcharge

logger = logging.getLogger('default')


def adjust_shopify_fees():
    qs = ProceedsAdjustment.objects.filter(date__gte='2016-11-24')
    qs = qs.filter(sale__paid_thru_id='SHOPIFY')
    qs = qs.filter(adjust_type="CHANNEL_FEES")

    for p in qs:
        if p.date == p.sale.sale_date:
            new_fees = Decimal((p.sale.taxable_proceeds() * Decimal('0.026') + Decimal('0.3')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            if new_fees > 0:
                p.amount = -new_fees
                p.save()


def backfill_FBA_fulfills():
    FBA_wh = inventory_api.warehouse('FBA', {})['id']
    FBA_shiptype = inventory_api.shippingtype('FBA', {})['id']
    inv_items = dict((i['label'], i['id']) for i in products_api.inventoryitem({}))

    unfld = fulfill_api.unfulfilled({})
    unfld_amzn = [s for s in unfld if s['channel'] == 'AMZN']

    for s in unfld_amzn:
        fulfill_info = {}
        fulfill_info['request_date'] = s['sale_date']
        fulfill_info['warehouse_id'] = FBA_wh
        fulfill_info['order_id'] = s['id']
        fulfill_info['status'] = 'requested'
        fulfill_info['bill_to'] = 'AMZN'
        fulfill_info['ship_type_id'] = FBA_shiptype

        fulfill_obj = Fulfillment(**fulfill_info)
        fulfill_obj.save()

        unfulfilled_items = fulfill_api.unfulfilled(str(s['id']), {})['unfulfilled_items']
        for label, quantity in unfulfilled_items.iteritems():
            fline_info = {}
            fline_info['inventory_item_id'] = inv_items[label]
            fline_info['quantity'] = quantity
            fline_info['fulfillment_id'] = fulfill_obj.id
            fline_obj = FulfillLine(**fline_info)
            fline_obj.save()
    return

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


def backfill_unitsale_dates():
    unit_sales = UnitSale.objects.all()
    for us in unit_sales:
        print 'working on', us.sale
        us.date = us.sale.sale_date
        us.save()

def backfill_salestax_dates():
    sales_taxes = SalesTax.objects.all()

    for st in sales_taxes:
        st.date = st.sale.sale_date
        st.save()
    

def backfill_channel_charge_proceeds():
    sales = Sale.objects.all()

    for s in sales:
        if s.channel_charges > Decimal('0'):
            pa = ProceedsAdjustment()
            pa.sale = s
            pa.date = s.sale_date
            pa.amount = s.channel_charges
            pa.adjust_type = 'CHANNEL_FEES'
            pa.save()
    
def backfill_shipping_charge_proceeds():
    sales = Sale.objects.all()

    for s in sales:
        if s.shipping_charge > Decimal('0'):
            pa = ProceedsAdjustment()
            pa.sale = s
            pa.date = s.sale_date
            pa.amount = s.shipping_charge
            pa.adjust_type = 'SHIPPING_CHARGE'
            pa.save()
    

def backfill_gift_wrap_fee_proceeds():
    sales = Sale.objects.all()

    for s in sales:
        if s.gift_wrap_fee > Decimal('0'):
            pa = ProceedsAdjustment()
            pa.sale = s
            pa.date = s.sale_date
            pa.amount = s.gift_wrap_fee
            pa.adjust_type = 'GIFTWRAP_FEES'
            pa.save()
    

def backfill_discount_proceeds():
    sales = Sale.objects.all()

    for s in sales:
        if s.discount > Decimal('0'):
            pa = ProceedsAdjustment()
            pa.sale = s
            pa.date = s.sale_date
            pa.amount = s.discount
            pa.adjust_type = 'DISCOUNT'
            pa.save()
