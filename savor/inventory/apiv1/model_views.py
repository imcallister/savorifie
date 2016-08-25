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
