from multipledispatch import dispatch

from django.db.models import Prefetch

from inventory.models import *
from inventory.serializers import *


@dispatch(dict)
def warehouse(qstring):
    qs = Warehouse.objects.all()
    return WarehouseSerializer(qs, many=True).data


@dispatch(str, dict)
def warehouse(label, qstring):
    qs = Warehouse.objects.filter(label=label).first()
    return WarehouseSerializer(qs).data


@dispatch(dict)
def product(qstring):
    qs = Product.objects.all().prefetch_related(Prefetch('skuunit'))
    return ProductSerializer(qs, many=True).data


@dispatch(str, dict)
def product(label, qstring):
    qs = Product.objects.filter(label=label).prefetch_related(Prefetch('skuunit_set')).first()
    return ProductSerializer(qs).data


@dispatch(dict)
def channelshipmenttype(qstring):
    qs = ChannelShipmentType.objects.all()
    return ChannelShipmentTypeSerializer(qs, many=True).data


@dispatch(str, dict)
def channelshipmenttype(label, qstring):
    qs = ChannelShipmentType.objects.filter(label=label).first()
    return ChannelShipmentTypeSerializer(qs).data


@dispatch(dict)
def shippingtype(qstring):
    qs = ShippingType.objects.all()
    return ShippingTypeSerializer(qs, many=True).data


@dispatch(str, dict)
def shippingtype(label, qstring):
    qs = ShippingType.objects.filter(label=label).first()
    return ShippingTypeSerializer(qs).data


@dispatch(dict)
def inventoryitem(qstring):
    qs = InventoryItem.objects.all().select_related('product_line')
    return InventoryItemSerializer(qs, many=True).data


@dispatch(str, dict)
def inventoryitem(label, qstring):
    qs = InventoryItem.objects.filter(label=label).first()
    return InventoryItemSerializer(qs).data
