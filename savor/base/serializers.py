from accountifie.common.serializers import EagerLoadingMixin

import models
from rest_framework import serializers


class UnitSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['sku__label', 'sku__description']
    sku = serializers.StringRelatedField()

    class Meta:
        model = models.UnitSale
        fields = ('id', 'sale', 'sku', 'quantity', 'unit_price')
   

class SimpleSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    items_string = serializers.SerializerMethodField()

    _SELECT_RELATED_FIELDS = ['channel__counterparty__id', 'channel', 'customer_code']
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item']

    def get_label(self, obj):
        return str(obj)

    def get_items_string(self, obj):
        return obj.items_string


    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = models.Sale
        fields = ('id', 'label', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'shipping_name',
                  'shipping_company', 'shipping_zip', 'items_string')


class SaleFulfillmentSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    items_string = serializers.SerializerMethodField()
    unfulfilled_items = serializers.SerializerMethodField()
    unfulfilled_string = serializers.SerializerMethodField()

    _SELECT_RELATED_FIELDS = ['channel__counterparty__id', 'channel', 'customer_code']
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item']

    def get_label(self, obj):
        return str(obj)

    def get_items_string(self, obj):
        return obj.items_string

    def get_unfulfilled_string(self, obj):
        return obj.unfulfilled_items_string

    def get_unfulfilled_items(self, obj):
        return obj.unfulfilled_items


    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = models.Sale
        fields = ('id', 'label', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'shipping_name', 'shipping_company',
                  'shipping_zip', 'items_string', 'unfulfilled_string', 'unfulfilled_items')


class ShippingSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):

    def get_label(self, obj):
        return str(obj)

    _SELECT_RELATED_FIELDS = ['channel__counterparty', 'customer_code']
    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = models.Sale
        fields = ('id', 'label', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'special_sale', 'discount',
                  'discount_code', 'gift_wrapping', 'gift_wrap_fee',
                  'gift_message', 'external_routing_id',
                  'shipping_charge', 'notification_email', 'shipping_name',
                  'shipping_company', 'shipping_address1', 'shipping_address2',
                  'shipping_city', 'shipping_zip', 'shipping_province',
                  'shipping_country', 'shipping_phone')


class FullSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    items_string = serializers.SerializerMethodField()

    def get_label(self, obj):
        return str(obj)

    def get_items_string(self, obj):
        return obj.items_string

    _SELECT_RELATED_FIELDS = ['company', 'channel__counterparty', 'ship_type', 'customer_code']
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item']
    company = serializers.StringRelatedField()
    channel = serializers.StringRelatedField()
    ship_type = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()
    unit_sale = UnitSaleSerializer(many=True)

    class Meta:
        model = models.Sale
        fields = ('id', 'label', 'company', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'special_sale', 'discount',
                  'discount_code', 'gift_wrapping', 'gift_wrap_fee',
                  'gift_message', 'ship_type', 'external_routing_id',
                  'shipping_charge', 'notification_email', 'shipping_name',
                  'shipping_company', 'shipping_address1', 'shipping_address2',
                  'shipping_city', 'shipping_zip', 'shipping_province',
                  'shipping_country', 'shipping_phone', 'items_string', 'unit_sale')
