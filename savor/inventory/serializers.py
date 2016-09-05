
from rest_framework import serializers

from accountifie.common.serializers import EagerLoadingMixin, AddressSerializer

import models


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


class ShipOptionSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['channel', 'ship_from', 'ship_type']

    ship_type = serializers.StringRelatedField()
    ship_from = serializers.StringRelatedField()
    channel = serializers.StringRelatedField()

    class Meta:
        model = models.ShipOption
        fields = ('id', 'label', 'ship_type', 'bill_to', 'use_pdf',
                  'packing_type', 'ship_from', 'channel')


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Warehouse
        fields = ('id', 'label', 'description',)
