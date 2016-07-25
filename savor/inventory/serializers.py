
from .models import Warehouse, Fulfillment, FulfillLine, InventoryItem
from rest_framework import serializers


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('label', 'description',)

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ('label', 'description', 'master_sku', 'product_line')


class FulfillLineSerializer(serializers.ModelSerializer):
    inventory_item = serializers.StringRelatedField()
    
    class Meta:
        model = FulfillLine
        fields = ('inventory_item', 'quantity')

class FulfillmentSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer(read_only=True)
    fulfill_lines = FulfillLineSerializer(many=True, read_only=True)

    class Meta:
        model = Fulfillment
        fields = ('request_date', 'warehouse', 'bill_to',
                  'use_pdf', 'packing_type', 'fulfill_lines')


