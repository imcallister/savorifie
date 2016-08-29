from multipledispatch import dispatch
from django.db.models import Sum, Prefetch

from .model_views import warehouse
from inventory.models import *
from fulfill.models import *


def inventorycount(qstring):
    sku_counts = ShipmentLine.objects \
                             .all() \
                             .values('inventory_item__label') \
                             .annotate(sku_count=Sum('quantity'))
    return dict((l['inventory_item__label'], l['sku_count']) for l in sku_counts)


def locationinventory(qstring):
    all_shipments = dict((wh['label'], {}) for wh in warehouse({}))

    shipment_qs = Shipment.objects.all() \
                                  .select_related('destination') \
                                  .prefetch_related(Prefetch('shipmentline_set__inventory_item'))
    for shpmnt in shipment_qs:
        location = shpmnt.destination.label
        
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
                                    .prefetch_related(Prefetch('fulfill_lines__inventory_item'))
    for fulfill in fulfill_qs:
        if fulfill.warehouse is None:
            continue
        location = fulfill.warehouse.label
        if location not in all_shipments:
            all_shipments[location] = {}

        amounts = dict((fl.inventory_item.label, fl.quantity) for fl in fulfill.fulfill_lines.all())
        for item in amounts:
            if item not in all_shipments[location]:
                all_shipments[location][item] = -amounts[item]
            else:
                all_shipments[location][item] -= amounts[item]

    return all_shipments
