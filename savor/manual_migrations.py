import logging
from decimal import Decimal

from sales.models import Sale
from accountifie.gl.models import Counterparty

from fulfill.models import WarehouseFulfill, Fulfillment, ShippingCharge
from sales.models import Payout, PayoutLine, UnitSale, SalesTax, ProceedsAdjustment
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


def backfill_unitsale_dates():
    unit_sales = UnitSale.objects.all()

    for us in unit_sales:
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
