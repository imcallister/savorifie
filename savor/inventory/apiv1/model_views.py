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
def shipoption(qstring):
    qs = ShipOption.objects.all()
    return ShipOptionSerializer(qs, many=True).data


@dispatch(str, dict)
def shipoption(label, qstring):
    qs = ShipOption.objects.filter(label=label).first()
    return ShipOptionSerializer(qs).data


@dispatch(dict)
def shippingtype(qstring):
    qs = ShippingType.objects.all()
    return ShippingTypeSerializer(qs, many=True).data


@dispatch(str, dict)
def shippingtype(label, qstring):
    qs = ShippingType.objects.filter(label=label).first()
    return ShippingTypeSerializer(qs).data
