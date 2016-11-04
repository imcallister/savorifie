from multipledispatch import dispatch
from django.db.models import Sum, Prefetch, F
from itertools import groupby

from .model_views import warehouse
from inventory.models import ShipmentLine, Shipment, InventoryTransfer, TransferLine
from fulfill.models import Fulfillment, FulfillLine


def inventorycount(qstring):
    sku_counts = ShipmentLine.objects \
                             .all() \
                             .values('inventory_item__label') \
                             .annotate(sku_count=Sum('quantity'))
    data = dict((l['inventory_item__label'], l['sku_count']) for l in sku_counts)

    return data


def shipmentline(qstring):
    shpmts = ShipmentLine.objects \
                         .annotate(inventory_item_label=F('inventory_item__label')) \
                         .annotate(shipment_label=F('shipment__label')) \
                         .all() \
                         .values()
    return list(shpmts)


@dispatch(unicode, dict)
def locationinventory(label, qstring):
    incoming_shipments =  ShipmentLine.objects.filter(shipment__destination__label=label) \
                                              .values('inventory_item__label', 'quantity')
    incoming_transfer = TransferLine.objects.filter(transfer__destination__label=label) \
                                            .values('inventory_item__label', 'quantity')
    outgoing_transfer = TransferLine.objects.filter(transfer__location__label=label) \
                                            .values('inventory_item__label', 'quantity')
    outgoing_fulfill = FulfillLine.objects.filter(fulfillment__warehouse__label=label) \
                                          .values('inventory_item__label', 'quantity')
    
    incoming = list(incoming_shipments) + list(incoming_transfer)
    outgoing = list(outgoing_transfer) + list(outgoing_fulfill)

    key_func = lambda x: x['inventory_item__label']
    
    incoming_counts = dict((k, sum(i['quantity'] for i in v)) for k,v in groupby(sorted(incoming, key=key_func), key=key_func))
    outgoing_counts = dict((k, sum(i['quantity'] for i in v)) for k,v in groupby(sorted(outgoing, key=key_func), key=key_func))

    total_counts = dict((k, incoming_counts.get(k) - outgoing_counts.get(k)) for k in list(set(incoming_counts.keys() + outgoing_counts.keys())))
    
    return total_counts


@dispatch(str, dict)
def locationinventory(label, qstring):
    incoming_shipments =  ShipmentLine.objects.filter(shipment__destination__label=label) \
                                              .values('inventory_item__label', 'quantity')
    incoming_transfer = TransferLine.objects.filter(transfer__destination__label=label) \
                                            .values('inventory_item__label', 'quantity')
    outgoing_transfer = TransferLine.objects.filter(transfer__location__label=label) \
                                            .values('inventory_item__label', 'quantity')
    outgoing_fulfill = FulfillLine.objects.filter(fulfillment__warehouse__label=label) \
                                          .values('inventory_item__label', 'quantity')
    
    incoming = list(incoming_shipments) + list(incoming_transfer)
    outgoing = list(outgoing_transfer) + list(outgoing_fulfill)

    key_func = lambda x: x['inventory_item__label']
    
    incoming_counts = dict((k, sum(i['quantity'] for i in v)) for k,v in groupby(sorted(incoming, key=key_func), key=key_func))
    outgoing_counts = dict((k, sum(i['quantity'] for i in v)) for k,v in groupby(sorted(outgoing, key=key_func), key=key_func))

    total_counts = dict((k, incoming_counts.get(k) - outgoing_counts.get(k)) for k in list(set(incoming_counts.keys() + outgoing_counts.keys())))
    
    return total_counts

@dispatch(dict)
def locationinventory(qstring):
    return dict((wh['label'], locationinventory(wh['label'], {})) for wh in warehouse({}))
