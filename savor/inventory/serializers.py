
from .models import Warehouse, Fulfillment, FulfillLine, InventoryItem, ShippingType, ChannelShipmentType
from rest_framework import serializers




class ShippingTypeSerializer(serializers.ModelSerializer):
    shipper = serializers.StringRelatedField()

    class Meta:
        model = ShippingType
        fields = ('id', 'label', 'description', 'shipper')




class ChannelShipmentTypeSerializer(serializers.ModelSerializer):
    ship_type = serializers.StringRelatedField()
    ship_from = serializers.StringRelatedField()
    channel = serializers.StringRelatedField()

    class Meta:
        model = ChannelShipmentType
        fields = ('id', 'label', 'ship_type', 'bill_to', 'use_pdf',
                  'packing_type', 'ship_from', 'channel')


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('id', 'label', 'description',)


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ('id', 'label', 'description', 'master_sku', 'product_line')


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


