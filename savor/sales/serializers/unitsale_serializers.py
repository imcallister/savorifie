
from accountifie.common.serializers import EagerLoadingMixin

from ..models import UnitSale
from rest_framework import serializers


class UnitSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['sku__label', 'sku__description']
    sku = serializers.StringRelatedField()

    class Meta:
        model = UnitSale
        fields = ('id', 'sale', 'sku', 'quantity', 'unit_price')


class UnitSaleItemSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['sku__label', 'sku__description', 'sale__sale_date']
    _PREFETCH_RELATED_FIELDS = ['sku__skuunit', 'sku__skuunit__inventory_item']
    
    items = serializers.SerializerMethodField()
    sale_date = serializers.SerializerMethodField()

    def get_items(self, obj):
        return dict((i.inventory_item.label, obj.quantity * i.quantity) for i in obj.sku.skuunit.all())

    def get_sale_date(self, obj):
        return obj.sale.sale_date

    class Meta:
        model = UnitSale
        fields = ('id', 'sale', 'sale_date', 'items', 'unit_price')

