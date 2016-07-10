from multipledispatch import dispatch

from django.forms.models import model_to_dict
from django.db.models import Prefetch

from accountifie.common.api import api_func
from inventory.models import *


def get_fields_and_properties(model, instance):
    field_names = [f.name for f in model._meta.fields]
    property_names = [name for name in dir(model) if isinstance(getattr(model, name), property)]
    return dict((name, getattr(instance, name)) for name in field_names + property_names)


def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data

@dispatch(dict)
def warehouse(qstring):
    all_warehouses = Warehouse.objects.all()
    return [get_model_data(obj, get_fields_and_properties(Warehouse, obj)) for obj in all_warehouses]


@dispatch(str, dict)
def warehouse(label, qstring):
    obj = Warehouse.objects.get(label=label)
    return get_model_data(obj, get_fields_and_properties(Warehouse, obj))


@dispatch(dict)
def product(qstring):
    all_skus = Product.objects.all().prefetch_related(Prefetch('skuunit_set', to_attr='skuunit'))
    skuunit_flds = get_fields_and_properties(SKUUnit, all_skus[0].skuunit[0])
    product_flds = get_fields_and_properties(Product, all_skus[0])

    data = []
    for sku in all_skus:
        skuunit_data = [get_model_data(unit, skuunit_flds) for unit in sku.skuunit]
        product_data = get_model_data(sku, product_flds)
        product_data.update({'sku_items': skuunit_data})
        data.append(product_data)

    return data


@dispatch(str, dict)
def product(label, qstring):
    sku = Product.objects.filter(label=label).prefetch_related(Prefetch('skuunit_set', to_attr='skuunit')).first()
    skuunit_flds = get_fields_and_properties(SKUUnit, sku.skuunit[0])
    product_flds = get_fields_and_properties(Product, sku)

    skuunit_data = [get_model_data(unit, skuunit_flds) for unit in sku.skuunit]
    product_data = get_model_data(sku, product_flds)
    product_data.update({'sku_items': skuunit_data})
    return product_data


@dispatch(dict)
def channelshipmenttype(qstring):
    all_types = list(ChannelShipmentType.objects.all())
    flds = get_fields_and_properties(ChannelShipmentType, all_types[0])
    return [get_model_data(t, flds) for t in all_types]


@dispatch(str, dict)
def channelshipmenttype(label, qstring):
    ship_info = ChannelShipmentType.objects.get(label=label)
    flds = get_fields_and_properties(ChannelShipmentType, ship_info)
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

    shipment_qs = Shipment.objects.all() \
                                  .select_related('destination') \
                                  .prefetch_related(Prefetch('shipmentline_set__inventory_item'))
    for shpmnt in shipment_qs:
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
    transfer_qs = InventoryTransfer.objects.all() \
                                           .prefetch_related(Prefetch('transferline_set__inventory_item'))
    for transfer in transfer_qs:
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
    fulfill_qs = Fulfillment.objects.all() \
                                    .select_related('warehouse') \
                                    .prefetch_related(Prefetch('fulfillline_set__inventory_item'))

    for fulfill in fulfill_qs:
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
    items = InventoryItem.objects.all().select_related('product_line')
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
