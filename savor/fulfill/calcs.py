from decimal import Decimal

from .models import ShippingCharge
import inventory.apiv1 as inventory_api

NC2_PER_FULFILL = Decimal('1.5')
NC2_PER_BOX = Decimal('0.5')

def create_nc2_shippingcharge(wh_flf):
    
    if wh_flf.fulfillment.ship_type.label == 'IFS_BEST':
        if ShippingCharge.objects.filter(external_id=wh_flf.tracking_number).count() == 0:
            # i.e. doesn't already exist
            chg = {}
            chg['shipper_id'] = inventory_api.shipper('IFS360', {})['id']
            chg['account'] = 'N/A'
            chg['tracking_number'] = wh_flf.tracking_number
            chg['external_id'] = wh_flf.tracking_number
            chg['invoice_number'] = wh_flf.warehouse_pack_id
            chg['ship_date'] = wh_flf.ship_date
            chg['charge'] = wh_flf.shipping_cost
            chg['fulfillment_id'] = wh_flf.fulfillment.id
            chg['order_related'] = True
            chg['comment'] = ''
            ShippingCharge(**chg).save()

    flf_str = 'FLF%s' % str(wh_flf.fulfillment.id)
    if ShippingCharge.objects.filter(external_id=flf_str).count() == 0:
        # create a fulfill level shipping charge
        chg = {}
        chg['shipper_id'] = inventory_api.shipper('IFS360', {})['id']
        chg['account'] = 'N/A'
        chg['tracking_number'] = wh_flf.tracking_number
        chg['external_id'] = flf_str
        chg['invoice_number'] = wh_flf.warehouse_pack_id
        chg['ship_date'] = wh_flf.ship_date
        chg['charge'] = NC2_PER_FULFILL
        chg['fulfillment_id'] = wh_flf.fulfillment.id
        chg['order_related'] = True
        chg['comment'] = ''
        ShippingCharge(**chg).save()

    if ShippingCharge.objects.filter(external_id=wh_flf.warehouse_pack_id).count() == 0:
        # create a box level shipping charge
        chg = {}
        chg['shipper_id'] = inventory_api.shipper('IFS360', {})['id']
        chg['account'] = 'N/A'
        chg['tracking_number'] = wh_flf.tracking_number
        chg['external_id'] = wh_flf.warehouse_pack_id
        chg['invoice_number'] = wh_flf.warehouse_pack_id
        chg['ship_date'] = wh_flf.ship_date
        chg['charge'] = NC2_PER_BOX
        chg['fulfillment_id'] = wh_flf.fulfillment.id
        chg['order_related'] = True
        chg['comment'] = ''
        ShippingCharge(**chg).save()

    return