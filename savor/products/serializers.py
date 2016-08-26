
from rest_framework import serializers

from accountifie.common.serializers import EagerLoadingMixin

import models


class ProductLineSerializer(serializers.ModelSerializer, EagerLoadingMixin):

    class Meta:
        model = models.ProductLine
        fields = ('id', 'label', 'description')


class InventoryItemSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['product_line']

    product_line = ProductLineSerializer(read_only=True)

    class Meta:
        model = models.InventoryItem
        fields = ('id', 'label', 'description', 'master_sku', 'product_line')


class SKUUnitSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['inventory_item']
    inventory_item = serializers.StringRelatedField()

    class Meta:
        model = models.SKUUnit
        fields = ('id', 'quantity', 'inventory_item', 'rev_percent')


class ProductSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _PREFETCH_RELATED_FIELDS = ['skuunit']
    skuunit = SKUUnitSerializer(read_only=True, many=True)

    class Meta:
        model = models.Product
        fields = ('id', 'label', 'description', 'skuunit')
