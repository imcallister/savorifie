
from accounting.models import COGSAssignment
from accounting.serializers import COGSAssignmentSerializer


def fifo_assignment(unit_sale_id, qstring):
    fifos = COGSAssignment.objects.filter(unit_sale_id=unit_sale_id)

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

def fifo_counts(qstring):
    qs = COGSAssignment.objects.all()
    qs = COGSAssignmentSerializer.setup_eager_loading(qs)
    data = COGSAssignmentSerializer(qs, many=True).data

    order_keys = list(set(row['shipment_label'] for row in data))
    item_keys = list(set(row['unit_label'] for row in data))

    tbl = []
    for o in order_keys:
        row = {'order': o}
        for i in item_keys:
          row[i] = sum([x['quantity'] for x in data if x['unit_label'] == i and x['shipment_label'] == o])
        tbl.append(row)
    return tbl


def cogsassignment(qstring):
    qs = COGSAssignment.objects.all()
    qs = COGSAssignmentSerializer.setup_eager_loading(qs)
    return COGSAssignmentSerializer(qs, many=True).data
