import logging

from sales.models import Sale
from fulfill.models import WarehouseFulfill, Fulfillment, ShippingCharge
from sales.importers.shopify import shopify_fee

from fulfill.calcs import create_nc2_shippingcharge

logger = logging.getLogger('default')

def add_shopify_fees():
    for s in Sale.objects.filter(channel__label='SHOPIFY'):
        s.channel_charges = shopify_fee(s)
        s.save()
    return

def backfill_nc2_shipcharges():
    # re-do for all NC2 fulfills

    NC2_flf = [wf['id'] for wf in Fulfillment.objects.filter(warehouse__label='NC2').values('id')]
    ShippingCharge.objects.filter(fulfillment__id__in=NC2_flf).delete()

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
