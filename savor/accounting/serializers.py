
from rest_framework import serializers

from accountifie.common.serializers import EagerLoadingMixin, AddressSerializer

import models


class COGSAssignmentSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['shipment_line__shipment', 'shipment_line__inventory_item', 'unit_sale__sale']
    
    shipment_label = serializers.SerializerMethodField()
    unit_label = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField() 
    
    def get_cost(self, obj):
        return obj.shipment_line.cost

    def get_shipment_label(self, obj):
        return obj.shipment_line.shipment.label

    def get_unit_label(self, obj):
        return obj.shipment_line.inventory_item.label

    def get_order_id(self, obj):
        return obj.unit_sale.sale.external_channel_id

    class Meta:
        model = models.COGSAssignment
        fields = ['id', 'shipment_label', 'quantity', 'cost', 'unit_label', 'order_id']

