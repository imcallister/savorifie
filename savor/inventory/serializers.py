
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
    
    class Meta:
        model = models.ShipOption
        fields = ('id', 'label', 'ship_type', 'bill_to', 'use_pdf',
                  'packing_type', 'ship_from')


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Warehouse
        fields = ('id', 'label', 'description',)


class ShipmentLineSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['inventory_item__product_line', 'inventory_item', 'shipment']

    unit_label = serializers.SerializerMethodField()
    productline = serializers.SerializerMethodField()
    shipment_label = serializers.SerializerMethodField()
    
    def get_unit_label(self, obj):
        return obj.inventory_item.label

    def get_productline(self, obj):
        return obj.inventory_item.product_line.label

    def get_shipment_label(self, obj):
        return obj.shipment.label

    class Meta:
        model = models.ShipmentLine
        fields = ('id', 'unit_label', 'quantity', 'shipment_label', 'productline')
