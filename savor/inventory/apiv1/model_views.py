from multipledispatch import dispatch

from django.forms.models import model_to_dict

from accountifie.common.api import api_func
from inventory.models import *


def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data

@dispatch(dict)
def warehouse(qstring):
    all_warehouses = Warehouse.objects.all()
    flds = ['id', 'label','description']
    return [get_model_data(obj, flds) for obj in all_warehouses]


@dispatch(str, dict)
def warehouse(label, qstring):
    warehouse = Warehouse.objects.get(label=label)
    flds = ['id', 'label','description']
    return get_model_data(warehouse, flds)


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
def product(label, qstring):
    sku = Product.objects.get(label=label)

    d = model_to_dict(sku)
    sku_items = list(sku.skuunit_set.all().values())

    for item in sku_items:
        inv_item = model_to_dict(InventoryItem.objects.get(id=item['inventory_item_id']))
        item.update(inv_item)
    d['sku_items'] = sku_items

    return d


@dispatch(dict)
def channelshipmenttype(qstring):
    flds = ['label', 'channel', 'ship_type', 'bill_to']
    all_types = list(ChannelShipmentType.objects.all())
    return [get_model_data(t, flds) for t in all_types]


@dispatch(str, dict)
def channelshipmenttype(label, qstring):
    flds = ['label', 'channel', 'ship_type', 'bill_to', 'use_pdf', 'packing_type']
    ship_info = ChannelShipmentType.objects.get(label=label)
    return get_model_data(ship_info, flds)

@dispatch(dict)
def shippingtype(qstring):
    flds = ['shipper', 'label', 'description', 'id']
    all_types = list(ShippingType.objects.all())
    return [get_model_data(t, flds) for t in all_types]


@dispatch(str, dict)
def shippingtype(label, qstring):
    flds = ['shipper', 'shipper_id', 'label', 'description', 'id']
    ship_info = ShippingType.objects.get(label=label)
    return get_model_data(ship_info, flds)



def inventorycount(qstring):
    all_shipments = {}
    for item in inventoryitem({}):
        all_shipments[item['label']] = sum([sl.quantity for sl in ShipmentLine.objects.filter(inventory_item_id=item['id'])])

    return all_shipments


def locationinventory(qstring):
    all_shipments = {}

    for shpmnt in Shipment.objects.all():
        location = shpmnt.destination.label
        if location not in all_shipments:
            all_shipments[location] = {}

        amounts = dict((sl.inventory_item.label, sl.quantity) for sl in shpmnt.shipmentline_set.all())
        for item in amounts:
            if item not in all_shipments[location]:
                all_shipments[location][item] = amounts[item]
            else:
                all_shipments[location][item] += amounts[item]

    # now subtract out any outgoing transfers and add incoming transfers
    for transfer in InventoryTransfer.objects.all():
        outgoing = transfer.location.label
        incoming = transfer.destination.label

        if outgoing not in all_shipments:
            all_shipments[outgoing] = {}

        if incoming not in all_shipments:
            all_shipments[incoming] = {}

        amounts = dict((tl.inventory_item.label, tl.quantity) for tl in transfer.transferline_set.all())
        for item in amounts:
            if item not in all_shipments[incoming]:
                all_shipments[incoming][item] = amounts[item]
            else:
                all_shipments[incoming][item] += amounts[item]

            if item not in all_shipments[outgoing]:
                all_shipments[outgoing][item] = -amounts[item]
            else:
                all_shipments[outgoing][item] -= amounts[item]

    # now remove fulfilled
    for fulfill in Fulfillment.objects.all():
        location = fulfill.warehouse.label
        if location not in all_shipments:
            all_shipments[location] = {}

        amounts = dict((fl.inventory_item.label, fl.quantity) for fl in fulfill.fulfillline_set.all())
        for item in amounts:
            if item not in all_shipments[location]:
                all_shipments[location][item] = -amounts[item]
            else:
                all_shipments[location][item] -= amounts[item]

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
def inventoryitem(label, qstring):
    item = InventoryItem.objects.get(label=label)
    product_line = item.product_line
    item_data = model_to_dict(item)
    product_line_data = dict(('Product Line %s' %k, v) for k,v in model_to_dict(product_line).iteritems())

    data = item_data
    data.update(product_line_data)
    return data
