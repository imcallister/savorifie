import itertools
from collections import Counter

from django.db.models import Sum

from accounting.models import COGSAssignment
from accounting.serializers import COGSAssignmentSerializer
from inventory.serializers import ShipmentLineSerializer
from inventory.models import ShipmentLine
import sales.apiv1 as sales_api
import inventory.apiv1 as inv_api



def fifo_counts(qstring):
    sl_data = inv_api.shipmentline({})
    assigned = COGSAssignment.objects.values('shipment_line') \
                                     .annotate(total=Sum('quantity'))

    shipment_keys = list(set(sl['shipment_label'] for sl in sl_data))
    item_keys = list(set(sl['unit_label'] for sl in sl_data))
    arrival_dates = dict((sl['shipment_label'], sl['arrival_date']) for sl in sl_data)

    table = []

    for sk in shipment_keys:
        row = {'order': sk, 'arrival_date': arrival_dates.get(sk)}
        for item in item_keys:
            
            try:
                sl = next((l for l in sl_data if l['shipment_label'] == sk and l['unit_label'] == item))
                row[item] = next((a for a in assigned if a['shipment_line'] == sl['id']))['total']
            except:
                row[item] = 0
        
        table.append(row)
    
    return sorted(table, key=lambda x: x['arrival_date'])


def fifo_available_shipmentlines(qstring, inventory_item):
    qs = ShipmentLine.objects.filter(inventory_item__label=inventory_item)
    shipments = sorted(ShipmentLineSerializer(qs, many=True).data, 
                                              key=lambda x: x['arrival_date'])
    shipline_ids = [s['id'] for s in shipments]

    assigned = dict((sl['shipment_line'], sl['total']) \
                    for sl in COGSAssignment.objects.filter(shipment_line_id__in=shipline_ids) \
                                                    .values('shipment_line') \
                                                    .annotate(total=Sum('quantity')))    

    for s in shipments:
        s.update({'available': s['quantity'] - assigned.get(s['id'], 0)})

    return [s for s in shipments if s['available'] > 0]


def fifo_available(qstring):
    sl_data = inv_api.shipmentline({})
    assigned = COGSAssignment.objects.values('shipment_line') \
                                     .annotate(total=Sum('quantity'))

    shipment_keys = list(set(sl['shipment_label'] for sl in sl_data))
    item_keys = list(set(sl['unit_label'] for sl in sl_data))
    
    table = []

    for sk in shipment_keys:
        ship_info = [i for i in sl_data if i['shipment_label'] == sk]
        row = {'order': sk, 'arrival_date': ship_info[0]['arrival_date']}

        for item in item_keys:
            try:
                sl = next((l for l in ship_info if l['unit_label'] == item))
                row[item] = sl['quantity']
                
                assgnds = [a for a in assigned if a['shipment_line'] == sl['id']]
                if len(assgnds) > 0:
                    row[item] -= assgnds[0]['total']
            except:
                row[item] = 0

        table.append(row)
    return sorted(table, key=lambda x: x['arrival_date'])


def fifo_unassigned(qstring):
    u_sales = sales_api.unitsaleitems({})
    
    def _diff(d1, d2):
        keys = list(set(d1.keys() + d2.keys()))
        output = dict((k, d1.get(str(k), 0) - d2.get(str(k), 0)) for k in keys)
        return dict((k, v) for k, v in output.iteritems() if v != 0)

    key_func2 = lambda x: x['unit_label']
    def _agg_items(lst):
        return dict((k, sum(l['quantity'] for l in v)) for k,v in itertools.groupby(sorted(lst, key=key_func2), key=key_func2))

    # group assigned by unit sale id
    key_func = lambda x: x['unitsale_id']
    assigned = dict((str(k), _agg_items(list(v))) \
                       for k,v in itertools.groupby(sorted(cogsassignment({}), key=key_func), key=key_func))

    for u in u_sales:
        u['unassigned'] = _diff(u['items'], assigned.get(str(u['id']), {}))

    return [u for u in u_sales if len(u['unassigned']) > 0]

def fifo_unassigned_count(qstring):
    unassigned = [e['unassigned'] for e in fifo_unassigned({})]
    return sum((Counter(d) for d in unassigned[1:]), Counter(unassigned[0]))


def cogsassignment(qstring):
    qs = COGSAssignment.objects.all()
    qs = COGSAssignmentSerializer.setup_eager_loading(qs)
    return COGSAssignmentSerializer(qs, many=True).data
