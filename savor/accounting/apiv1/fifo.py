import json

from django.core.serializers.json import DjangoJSONEncoder

import accounting.models


def fifo_assignment(unit_sale_id, qstring):
    fifos = accounting.models.COGSAssignment.objects.filter(unit_sale_id=unit_sale_id)

    def get_data(obj):
        data = {}
        data['shipment_line'] = str(obj.shipment_line)
        data['shipment_line_id'] = obj.shipment_line.id
        data['unit_sale'] = str(obj.unit_sale)
        data['unit_sale_id'] = obj.unit_sale.id
        data['quantity'] = obj.quantity
        data['sku'] = obj.shipment_line.inventory_item.label
        return data

    return [get_data(obj) for obj in fifos]
