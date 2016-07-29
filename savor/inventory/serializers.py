
from .models import *
from base.serializers import SimpleSaleSerializer
from rest_framework import serializers


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ('id', 'label', 'description', 'master_sku', 'product_line')


class SKUUnitSerializer(serializers.ModelSerializer):
    inventory_item = serializers.StringRelatedField()

    class Meta:
        model = SKUUnit
        fields = ('id', 'quantity', 'inventory_item', 'rev_percent')


class ProductSerializer(serializers.ModelSerializer):
    skuunit = SKUUnitSerializer(read_only=True, many=True)

    class Meta:
        model = Product
        fields = ('id', 'label', 'description', 'skuunit')


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


class FulfillUpdateSerializer(serializers.ModelSerializer):
    shipper = serializers.StringRelatedField()

    class Meta:
        model = FulfillUpdate
        fields = ('update_date', 'comment', 'status',
                  'shipper', 'tracking_number')


class FulfillLineSerializer(serializers.ModelSerializer):
    inventory_item = serializers.StringRelatedField()

    class Meta:
        model = FulfillLine
        fields = ('inventory_item', 'quantity')


class FulfillmentSerializer(serializers.ModelSerializer):
    warehouse = serializers.StringRelatedField()
    ship_type = serializers.StringRelatedField()
    fulfill_lines = FulfillLineSerializer(many=True, read_only=True)
    fulfill_updates = FulfillUpdateSerializer(many=True, read_only=True)
    order = SimpleSaleSerializer(read_only=True)

    class Meta:
        model = Fulfillment
        fields = ('id', 'order', 'request_date', 'status', 'warehouse',
                  'bill_to', 'ship_type',
                  'use_pdf', 'packing_type', 'fulfill_lines', 'fulfill_updates')


class BatchRequestSerializer(serializers.ModelSerializer):
    location = serializers.StringRelatedField()
    fulfillments = FulfillmentSerializer(many=True, read_only=True)

    class Meta:
        model = BatchRequest
        fields = ('id', 'created_date', 'location',
                  'fulfillments', 'comment',)


class WarehouseFulfillLineSerializer(serializers.ModelSerializer):
    inventory_item = serializers.StringRelatedField()

    class Meta:
        model = WarehouseFulfillLine
        fields = ('inventory_item', 'quantity',)


class WarehouseFulfillSerializer(serializers.ModelSerializer):
    savor_order = SimpleSaleSerializer(read_only=True)
    savor_transfer = serializers.StringRelatedField()
    warehouse = serializers.StringRelatedField()
    shipping_type = serializers.StringRelatedField()
    fulfill_lines = WarehouseFulfillLineSerializer(many=True, read_only=True)

    class Meta:
        model = WarehouseFulfill
        flds = ('savor_order', 'savor_transfer', 'warehouse', 'fulfill_lines',
                'warehouse_pack_id', 'order_date', 'request_date',
                'ship_date', 'shipping_name', 'shipping_attn', 'shipping_address1',
                'shipping_address2', 'shipping_address3', 'shipping_city',
                'shipping_zip', 'shipping_province', 'shipping_country',
                'shipping_phone', 'ship_email', 'shipping_type', 'tracking_number')
