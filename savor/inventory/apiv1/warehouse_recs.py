
from accountifie.common.api import api_func



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
            if whouse_record['skus'] != unfld['skus'] or order_data['shipping_zip'] != whouse_record['shipping_zip']:
                mismatched.append({'savor': order_data, 'thoroughbred': whouse_recs})

    return mismatched
