from multipledispatch import dispatch

from django.db.models import Prefetch

from .models import Product, InventoryItem
from .serializers import ProductSerializer, InventoryItemSerializer


@dispatch(dict)
def product(qstring):
    qs = Product.objects.all().prefetch_related(Prefetch('skuunit'))
    return ProductSerializer(qs, many=True).data


@dispatch(str, dict)
def product(label, qstring):
    qs = Product.objects.filter(label=label).prefetch_related(Prefetch('skuunit_set')).first()
    return ProductSerializer(qs).data


@dispatch(dict)
def inventoryitem(qstring):
    qs = InventoryItem.objects.all().select_related('product_line')
    return InventoryItemSerializer(qs, many=True).data


@dispatch(str, dict)
def inventoryitem(label, qstring):
    qs = InventoryItem.objects.filter(label=label).first()
    return InventoryItemSerializer(qs).data
