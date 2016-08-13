from multipledispatch import dispatch

from accountifie.common.api import api_func
from inventory.models import WarehouseFulfill, Fulfillment


def rec_zip(z1, z2):
    # deal with the dropped leading zero issue
    if len(z1)==4 and len(z2)==5 and z2[0]=='0':
        return (z1 == z2[1:])
    elif len(z2)==4 and len(z1)==5 and z1[0]=='0':
        return (z2 == z1[1:])
    else:
        return (z2==z1)

@dispatch(dict)
def thoroughbred_mismatch(qstring):
    mismatched_f = api_func('inventory',
                           'fulfillment',
                           qstring={'status': 'mismatched'})
    warehouse_recds = api_func('inventory', 'warehousefulfill')
    mismatched = []
    for f in mismatched_f:
        fulfill_id = f['id']
        order_zip = f['order']['shipping_zip']
        whouse_recs = [r for r in warehouse_recds
                       if r['fulfillment'] == fulfill_id]

        if len(whouse_recs) > 0:
            whouse_record = whouse_recs[0]

            if whouse_record['skus'] != f['skus']:
                mismatched.append({'fulfill_id': fulfill_id,
                                   'fail_reason': 'SKUS'})
            elif not rec_zip(order_zip,
                             whouse_record['shipping_zip']):
                mismatched.append({'fulfill_id': fulfill_id,
                                   'fail_reason': 'ZIP'})

    return mismatched

@dispatch(str, dict)
def thoroughbred_mismatch(order_id, qstring):
    order_data = api_func('base', 'sale', order_id)
    # for now assume only ever one fulfill
    wh_fulfill = WarehouseFulfill.objects \
                                 .filter(savor_order_id=order_id) \
                                 .values('warehouse_pack_id')[0]

    req_fulfill = Fulfillment.objects \
                             .filter(order_id=order_id) \
                             .values('id')[0]

    req_record = api_func('inventory', 'fulfillment', req_fulfill['id'])
    req_record['shipping_zip'] = order_data['shipping_zip']
    req_record['shipping_name'] = order_data['shipping_name']
    whouse_record = api_func('inventory', 'warehousefulfill', wh_fulfill['warehouse_pack_id'])

    output = []
    flds = ['shipping_name', 'shipping_zip', 'skus']

    def get_row(fld):
        return {'field': fld,
                'savor': str(req_record.get(fld, '')),
                'thoroughbred': str(whouse_record.get(fld, '')),
                'mismatch': req_record.get(fld, '') != whouse_record.get(fld, '')}

    for fld in flds:
        output.append(get_row(fld))

    return output
