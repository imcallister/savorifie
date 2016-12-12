import itertools
from collections import Counter

from accounting.models import COGSAssignment
from accounting.serializers import COGSAssignmentSerializer
import sales.apiv1 as sales_api
import inventory.apiv1 as inv_api



def fifo_counts(qstring):
    qs = COGSAssignment.objects.all()
    qs = COGSAssignmentSerializer.setup_eager_loading(qs)
    data = COGSAssignmentSerializer(qs, many=True).data

    order_keys = list(set(row['shipment_label'] for row in data))
    item_keys = list(set(row['unit_label'] for row in data))

    ship_cnts = inv_api.shipmentcounts({})
    arrival_dates = dict((sl['order'], sl['arrival_date']) for sl in ship_cnts)

    tbl = []
    for o in order_keys:
        row = {'order': o, 'arrival_date': arrival_dates.get(o)}
        for i in item_keys:
          row[i] = sum([x['quantity'] for x in data if x['unit_label'] == i and x['shipment_label'] == o])
        tbl.append(row)
    return sorted(tbl, key=lambda x: x['arrival_date'])

def fifo_unassigned(qstring):
    u_sales = sales_api.unitsaleitems({})
    
    def _diff(d1, d2):
        keys = list(set(d1.keys() + d2.keys()))
        output = dict((k, d1.get(str(k), 0) - d2.get(str(k), 0)) for k in keys)
        return dict((k, v) for k, v in output.iteritems() if v != 0)

    # group assigned by unit sale id
    key_func = lambda x: x['unitsale_id']
    assigned = dict((str(k), dict((l['unit_label'], l['quantity']) for l in v)) \
                       for k,v in itertools.groupby(sorted(cogsassignment({}), key=key_func), key=key_func))

    for u in u_sales:
        u['unassigned'] = _diff(u['items'], assigned.get(str(u['id']), {}))

    return [u for u in u_sales if len(u['unassigned']) > 0]

def fifo_unassigned_count(qstring):
    unassigned = [e['unassigned'] for e in fifo_unassigned({})]
    return sum((Counter(d) for d in unassigned[1:]), Counter(unassigned[0]))


def fifo_available(qstring):
    ship_cnts = inv_api.shipmentcounts({})
    fifo_cnts = fifo_counts({})

    orders = list(set([x['order'] for x in fifo_cnts] + [x['order'] for x in ship_cnts]))
    items =  list(set(list(itertools.chain.from_iterable([d.keys() for d in ship_cnts])) + 
                      list(itertools.chain.from_iterable([d.keys() for d in fifo_cnts]))))
    items.remove('order')
    items.remove('arrival_date')

    arrival_dates = dict((sl['order'], sl['arrival_date']) for sl in ship_cnts)
    
    available = []
    for order in orders:
        row = {'order': order, 'arrival_date': arrival_dates.get(order)}
        ship_cnt = next((x for x in ship_cnts if x['order'] == order), {})
        fifo_cnt = next((x for x in fifo_cnts if x['order'] == order), {})
        row.update(dict((item, ship_cnt.get(item, 0) - fifo_cnt.get(item, 0)) for item in items))
        available.append(row)
    
    return sorted(available, key=lambda x: x['arrival_date'])
            




def cogsassignment(qstring):
    qs = COGSAssignment.objects.all()
    qs = COGSAssignmentSerializer.setup_eager_loading(qs)
    return COGSAssignmentSerializer(qs, many=True).data
