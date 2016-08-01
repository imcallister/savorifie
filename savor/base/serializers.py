from accountifie.common.serializers import EagerLoadingMixin

from .models import *
from rest_framework import serializers


class SimpleSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['channel', 'customer_code']

    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = Sale
        fields = ('id', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'shipping_name',
                  'shipping_company', 'shipping_zip')


class FullSaleSerializer(serializers.ModelSerializer):
    _SELECT_RELATED_FIELDS = ['company', 'channel', 'ship_type', 'customer_code']
    company = serializers.StringRelatedField()
    channel = serializers.StringRelatedField()
    ship_type = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = Sale
        fields = ('id', 'company', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'special_sale', 'discount',
                  'discount_code', 'gift_wrapping', 'gift_wrap_fee',
                  'gift_message', 'ship_type', 'external_routing_id',
                  'shipping_charge', 'notification_email', 'shipping_name',
                  'shipping_company', 'shipping_address1', 'shipping_address2',
                  'shipping_city', 'shipping_zip', 'shipping_province',
                  'shipping_country', 'shipping_phone')
