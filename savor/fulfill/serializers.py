
from rest_framework import serializers

from accountifie.common.serializers import EagerLoadingMixin, AddressSerializer

import models
import sales.serializers as salesslz
import inventory.serializers as invslz



class ShippingChargeSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['fulfillment', 'fulfillment__order__channel__counterparty', 
                              'shipper__company', 'fulfillment__warehouse',
                              'fulfillment__ship_type', 'fulfillment__bill_to'
                              ]
    fulfillment = serializers.StringRelatedField()
    fulfillment_id = serializers.SerializerMethodField()
    warehouse = serializers.SerializerMethodField()
    requested_ship_type = serializers.SerializerMethodField()
    shipper = serializers.StringRelatedField()

    def get_warehouse(self, obj):
        if obj.fulfillment:
            return str(obj.fulfillment.warehouse)
        else:
            return ''

    def get_fulfillment_id(self, obj):
        if obj.fulfillment:
            return str(obj.fulfillment.id)
        else:
            return

    def get_requested_ship_type(self, obj):
        if obj.fulfillment:
            return '%s: %s' % (str(obj.fulfillment.ship_type), obj.fulfillment.bill_to)
        else:
            return ''

    class Meta:
        model = models.ShippingCharge
        fields = ('shipper', 'account', 'tracking_number', 'invoice_number',
                  'ship_date', 'charge', 'order_related', 'external_id', 'comment', 'packing_id',
                  'fulfillment', 'fulfillment_id', 'requested_ship_type', 'warehouse')


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
    ship_type = invslz.ShippingTypeSerializer()
    fulfill_lines = FulfillLineSerializer(many=True, read_only=True)
    order = salesslz.ShippingSaleSerializer(read_only=True)
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
    _PREFETCH_RELATED_FIELDS = ['fulfill_lines', 'warehousefulfill',
                                'fulfill_lines__inventory_item',
                                ]

    warehouse = serializers.StringRelatedField()
    ship_type = invslz.ShippingTypeSerializer()
    fulfill_lines = FulfillLineSerializer(many=True, read_only=True)
    order = salesslz.ShippingSaleSerializer(read_only=True)
    ship_from = AddressSerializer(read_only=True)
    items_string = serializers.SerializerMethodField()

    def get_items_string(self, obj):
        return obj.items_string

    class Meta:
        model = models.Fulfillment
        fields = ('id', 'order', 'request_date', 'status',
                  'ship_info', 'warehouse', 'bill_to', 'ship_type',
                  'use_pdf', 'packing_type', 'fulfill_lines',
                  'ship_from', 'items_string',
                  )


class FullFulfillmentSerializer2(serializers.ModelSerializer, EagerLoadingMixin):
    def get_ship_info(self, obj):
        return obj.ship_info

    _SELECT_RELATED_FIELDS = ['order', 'warehouse', 'ship_type', 'ship_from',
                              'order__channel__counterparty', 'order__customer_code',
                              'ship_type__shipper__company']
    _PREFETCH_RELATED_FIELDS = ['fulfill_lines', 'warehousefulfill',
                                'fulfill_lines__inventory_item',
                                ]

    warehouse = serializers.StringRelatedField()
    ship_type = invslz.ShippingTypeSerializer()
    fulfill_lines = FulfillLineSerializer(many=True, read_only=True)
    order = salesslz.ShippingSaleSerializer(read_only=True)
    ship_from = AddressSerializer(read_only=True)
    items_string = serializers.SerializerMethodField()
    warehousefulfill_count = serializers.IntegerField(source='warehousefulfill.count', read_only=True)

    def get_items_string(self, obj):
        return obj.items_string

    class Meta:
        model = models.Fulfillment
        fields = ('id', 'order', 'request_date', 'status',
                  'ship_info', 'warehouse', 'bill_to', 'ship_type',
                  'use_pdf', 'packing_type', 'fulfill_lines',
                  'ship_from', 'items_string', 'warehousefulfill_count',
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
                              'savor_order__channel', 'savor_order__channel__counterparty', 
                              'warehouse', 'shipping_type']
    _PREFETCH_RELATED_FIELDS = ['fulfill_lines', 'fulfill_lines__inventory_item']
    _PREFETCH_RELATED_FIELDS += ['savor_order__unit_sale__sku__skuunit__inventory_item']

    savor_order = salesslz.SimpleSaleSerializer(read_only=True)
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
