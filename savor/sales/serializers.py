from django.utils.safestring import mark_safe

from accountifie.common.serializers import EagerLoadingMixin

from .models import UnitSale, Sale, SalesTax
from rest_framework import serializers


class UnitSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['sku__label', 'sku__description']
    sku = serializers.StringRelatedField()

    class Meta:
        model = UnitSale
        fields = ('id', 'sale', 'sku', 'quantity', 'unit_price')


class SalesTaxSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['sale__channel__counterparty__id', 'collector__entity']

    sale_date = serializers.SerializerMethodField()
    sale = serializers.StringRelatedField()
    collector = serializers.StringRelatedField()

    def get_sale_date(self, obj):
        return obj.sale.sale_date

    class Meta:
        model = SalesTax
        fields = ('sale_date', 'sale', 'collector', 'tax',)


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
        model = Sale
        fields = ('id', 'label', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'shipping_name',
                  'shipping_company', 'shipping_zip', 'items_string')


class SaleFulfillmentSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    items_string = serializers.SerializerMethodField()
    unfulfilled_items = serializers.SerializerMethodField()
    unfulfilled_string = serializers.SerializerMethodField()
    drilldown = serializers.SerializerMethodField()
    fulfillment_ids = serializers.SerializerMethodField()

    _SELECT_RELATED_FIELDS = ['channel__counterparty__id', 'channel', 'customer_code']
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item', 'fulfillments__fulfill_lines__inventory_item']

    def get_label(self, obj):
        return str(obj)

    def get_items_string(self, obj):
        return obj.items_string

    def get_unfulfilled_string(self, obj):
        return obj.unfulfilled_items_string

    def get_unfulfilled_items(self, obj):
        return obj.unfulfilled_items

    def get_fulfillment_ids(self, obj):
        return [f.id for f in obj.fulfillments.all()]

    def get_drilldown(self, obj):
        return mark_safe('<a href="/order/drilldown/%s">%s</a>' % (obj.id, obj.label))

    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = Sale
        fields = ('id', 'label', 'customer_code', 'channel', 'sale_date', 'drilldown',
                  'external_channel_id', 'shipping_name', 'shipping_company',
                  'shipping_zip', 'items_string', 'unfulfilled_string', 'unfulfilled_items',
                  'fulfillment_ids', 'gift_wrapping'
                  )


class ShippingSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):

    def get_label(self, obj):
        return str(obj)

    _SELECT_RELATED_FIELDS = ['channel__counterparty', 'customer_code']
    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = Sale
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

    _SELECT_RELATED_FIELDS = ['company', 'channel__counterparty', 'customer_code']
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item']
    company = serializers.StringRelatedField()
    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()
    unit_sale = UnitSaleSerializer(many=True)

    class Meta:
        model = Sale
        fields = ('id', 'label', 'company', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'special_sale', 'discount',
                  'discount_code', 'gift_wrapping', 'gift_wrap_fee',
                  'gift_message', 'external_routing_id',
                  'shipping_charge', 'notification_email', 'shipping_name',
                  'shipping_company', 'shipping_address1', 'shipping_address2',
                  'shipping_city', 'shipping_zip', 'shipping_province',
                  'shipping_country', 'shipping_phone', 'items_string', 'unit_sale')
