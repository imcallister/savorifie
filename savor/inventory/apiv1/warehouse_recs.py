
from accountifie.common.api import api_func


def rec_zip(z1, z2):
    # deal with the dropped leading zero issue
    if len(z1)==4 and len(z2)==5 and z2[0]=='0':
        return (z1 == z2[1:])
    elif len(z2)==4 and len(z1)==5 and z1[0]=='0':
        return (z2 == z1[1:])
    else:
        return (z2==z1)


def thoroughbred_mismatch(qstring):

    unfulfilled = api_func('inventory', 'fulfillment', qstring={'status': 'requested'})
    unfulfilled += api_func('inventory', 'fulfillment', qstring={'status': 'partial'})
    warehouse_recds = api_func('inventory', 'warehousefulfill')

    mismatched = []
    for unfld in unfulfilled:
        order_id = unfld['order_id']
        order_data = api_func('base', 'sale', order_id)
        whouse_recs = [r for r in warehouse_recds if r['savor_order_id']==order_id]
        if len(whouse_recs)>0:
            whouse_record = whouse_recs[0]
            if whouse_record['skus'] != unfld['skus'] or \
               not rec_zip(order_data['shipping_zip'], whouse_record['shipping_zip']):
                mismatched.append({'savor': order_data, 'thoroughbred': whouse_recs})

    return mismatched
