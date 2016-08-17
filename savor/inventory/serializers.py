
from rest_framework import serializers

from accountifie.common.serializers import EagerLoadingMixin, AddressSerializer

import models
import savor.base.serializers as baseslz


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


class ShipperSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['company']
    company = serializers.StringRelatedField()

    class Meta:
        model = models.Shipper
        fields = ['id', 'company']

class ShippingTypeSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['shipper__counterparty']
    shipper = ShipperSerializer(read_only=True)

    class Meta:
        model = models.ShippingType
        fields = ('id', 'label', 'description', 'shipper')


class ChannelShipmentTypeSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['channel', 'ship_from', 'ship_type']

    ship_type = serializers.StringRelatedField()
    ship_from = serializers.StringRelatedField()
    channel = serializers.StringRelatedField()

    class Meta:
        model = models.ChannelShipmentType
        fields = ('id', 'label', 'ship_type', 'bill_to', 'use_pdf',
                  'packing_type', 'ship_from', 'channel')


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Warehouse
        fields = ('id', 'label', 'description',)


class FulfillUpdateSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['shipper']
    shipper = serializers.StringRelatedField()

    class Meta:
        model = models.FulfillUpdate
        fields = ('update_date', 'comment', 'status',
                  'shipper', 'tracking_number')


class FulfillLineSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['inventory_item']
    inventory_item = serializers.StringRelatedField()

    class Meta:
        model = models.FulfillLine
        fields = ('inventory_item', 'quantity')


class FulfillmentSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    def get_ship_info(self, obj):
        return obj.ship_info

    _SELECT_RELATED_FIELDS = ['order', 'warehouse', 'ship_type', 'ship_from',
                              'order__channel__counterparty', 'order__customer_code',
                              'ship_type__shipper__company']
    _PREFETCH_RELATED_FIELDS = ['fulfill_lines',
                                'fulfill_lines__inventory_item']

    warehouse = serializers.StringRelatedField()
    ship_type = ShippingTypeSerializer()
    fulfill_lines = FulfillLineSerializer(many=True, read_only=True)
    order = baseslz.ShippingSaleSerializer(read_only=True)
    ship_from = AddressSerializer(read_only=True)

    class Meta:
        model = models.Fulfillment
        fields = ('id', 'order', 'request_date', 'status',
                  'ship_info', 'warehouse', 'bill_to', 'ship_type',
                  'use_pdf', 'packing_type', 'fulfill_lines',
                  'ship_from'
                  )


class FullFulfillmentSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    def get_ship_info(self, obj):
        return obj.ship_info

    _SELECT_RELATED_FIELDS = ['order', 'warehouse', 'ship_type', 'ship_from',
                              'order__channel__counterparty', 'order__customer_code',
                              'ship_type__shipper__company']
    _PREFETCH_RELATED_FIELDS = ['fulfill_lines',
                                'fulfill_lines__inventory_item',
                                'fulfill_updates__shipper__company']

    warehouse = serializers.StringRelatedField()
    ship_type = ShippingTypeSerializer()
    fulfill_lines = FulfillLineSerializer(many=True, read_only=True)
    fulfill_updates = FulfillUpdateSerializer(many=True, read_only=True)
    order = baseslz.ShippingSaleSerializer(read_only=True)
    ship_from = AddressSerializer(read_only=True)
    items_string = serializers.SerializerMethodField()

    def get_items_string(self, obj):
        return obj.items_string

    class Meta:
        model = models.Fulfillment
        fields = ('id', 'order', 'request_date', 'status',
                  'ship_info', 'warehouse', 'bill_to', 'ship_type',
                  'use_pdf', 'packing_type', 'fulfill_lines',
                  'ship_from', 'fulfill_updates', 'items_string'
                  )

class SimpleBatchRequestSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['location']
    _PREFETCH_RELATED_FIELDS = ['fulfillments']

    location = serializers.StringRelatedField()

    def get_fulfillment_count(self, obj):
        return obj.fulfillments.count()

    class Meta:
        model = models.BatchRequest
        fields = ('id', 'created_date', 'location',
                  'fulfillment_count', 'comment',)


class BatchRequestSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['location']
    _PREFETCH_RELATED_FIELDS = ['fulfillments'] + ['fulfillments__fulfill_lines', 'fulfillments__order__channel__counterparty',
                                                    'fulfillments__order__customer_code', 'fulfillments__ship_from',
                                                    'fulfillments__ship_type__shipper__company', 'fulfillments__warehouse',
                                                    'fulfillments__fulfill_lines__inventory_item']

    location = serializers.StringRelatedField()
    fulfillments = FulfillmentSerializer(many=True, read_only=True)

    class Meta:
        model = models.BatchRequest
        fields = ('id', 'created_date', 'location',
                  'fulfillments', 'comment',)


class WarehouseFulfillLineSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['inventory_item']
    inventory_item = serializers.StringRelatedField()

    class Meta:
        model = models.WarehouseFulfillLine
        fields = ('inventory_item', 'quantity',)


class WarehouseFulfillSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['savor_order', 'savor_transfer', 'savor_order__customer_code',
                              'savor_order__channel', 'savor_order__channel__counterparty__id', 
                              'warehouse', 'shipping_type']
    _PREFETCH_RELATED_FIELDS = ['fulfill_lines', 'fulfill_lines__inventory_item']
    _PREFETCH_RELATED_FIELDS += ['savor_order__unit_sale__sku__skuunit__inventory_item']

    savor_order = baseslz.SimpleSaleSerializer(read_only=True)
    savor_transfer = serializers.StringRelatedField()
    warehouse = serializers.StringRelatedField()
    shipping_type = serializers.StringRelatedField()
    fulfill_lines = WarehouseFulfillLineSerializer(many=True, read_only=True)

    class Meta:
        model = models.WarehouseFulfill
        flds = ('fulfillment_id', 'savor_order', 'savor_transfer', 'warehouse', 'fulfill_lines',
                'warehouse_pack_id', 'order_date', 'request_date',
                'ship_date', 'shipping_name', 'shipping_attn', 'shipping_address1',
                'shipping_address2', 'shipping_address3', 'shipping_city',
                'shipping_zip', 'shipping_province', 'shipping_country',
                'shipping_phone', 'ship_email', 'shipping_type', 'tracking_number')
