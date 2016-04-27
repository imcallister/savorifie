from multipledispatch import dispatch

from django.forms.models import model_to_dict

from accountifie.common.api import api_func
from inventory.models import *


def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data


@dispatch(dict)
def product(qstring):
    all_skus = Product.objects.all()
    data = []
    for sku in all_skus:
        d = model_to_dict(sku)
        sku_items = list(sku.skuunit_set.all().values())

        for item in sku_items:
            inv_item = model_to_dict(InventoryItem.objects.get(id=item['inventory_item_id']))
            item.update(inv_item)

        d['sku_items'] = sku_items
        data.append(d)
    return data


@dispatch(str, dict)
def product(short_code, qstring):
    sku = Product.objects.get(short_code=short_code)

    d = model_to_dict(sku)
    sku_items = list(sku.skuunit_set.all().values())

    for item in sku_items:
        inv_item = model_to_dict(InventoryItem.objects.get(id=item['inventory_item_id']))
        item.update(inv_item)
    d['sku_items'] = sku_items

    return d


@dispatch(dict)
def channelshipmenttype(qstring):
    flds = ['short_code', 'channel', 'ship_type', 'bill_to']
    all_types = list(ChannelShipmentType.objects.all())
    return [get_model_data(t, flds) for t in all_types]


@dispatch(str, dict)
def channelshipmenttype(short_code, qstring):
    flds = ['short_code', 'channel', 'ship_type', 'bill_to']
    ship_info = ChannelShipmentType.objects.get(short_code=short_code)
    return get_model_data(ship_info, flds)



def inventorycount(qstring):
    all_shipments = {}
    for item in inventoryitem({}):
        all_shipments[item['short_code']] = sum([sl.quantity for sl in ShipmentLine.objects.filter(inventory_item_id=item['id'])])

    return all_shipments


def locationinventory(qstring):
    all_shipments = {}

    for shpmnt in Shipment.objects.all():
        location = shpmnt.destination.short_code
        if location not in all_shipments:
            all_shipments[location] = {}

        amounts = dict((sl.inventory_item.short_code, sl.quantity) for sl in shpmnt.shipmentline_set.all())
        for item in amounts:
            if item not in all_shipments[location]:
                all_shipments[location][item] = amounts[item]
            else:
                all_shipments[location][item] += amounts[item]

    return all_shipments


@dispatch(dict)
def inventoryitem(qstring):
    items = InventoryItem.objects.all()
    all_data = []

    for item in items:
        product_line = item.product_line
        item_data = model_to_dict(item)
        product_line_data = dict(('Product Line %s' %k, v) for k,v in model_to_dict(product_line).iteritems())

        data = item_data
        data.update(product_line_data)
        all_data.append(data)

    return all_data


@dispatch(str, dict)
def inventoryitem(short_code, qstring):
    item = InventoryItem.objects.get(short_code=short_code)
    product_line = item.product_line
    item_data = model_to_dict(item)
    product_line_data = dict(('Product Line %s' %k, v) for k,v in model_to_dict(product_line).iteritems())

    data = item_data
    data.update(product_line_data)
    return data
