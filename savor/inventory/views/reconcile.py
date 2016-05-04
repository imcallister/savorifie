from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect

from accountifie.common.api import api_func
from fulfill_requests import post_fulfill_update

@login_required
def reconcile_warehouse(request):
    # for all fulfillments that are not completed
    # find the warehouse record and do reconciliation

    # reconcile:
    # 1: items match ...
    # 2: zip matches (?)
    # 3: shiping method matches
    # 4: store info in fulmfillment request and set status
    # there are unfulfilled sales.. want unfulfilled
    unfulfilled = api_func('inventory', 'fulfillment', qstring={'status': 'requested'})
    unfulfilled += api_func('inventory', 'fulfillment', qstring={'status': 'partial'})

    start_unfulfill = len(unfulfilled)
    new_fulfilled = 0
    mismatch_fulfills = 0

    mismatched = []

    warehouse_recds = api_func('inventory', 'warehousefulfill')
    # for each unfulfilled order look for an update in WarehouseFulfill which matches the order_id
    #   check that the number of items matches between fulfillment lines and 

    for unfld in unfulfilled:
        order_id = unfld['order_id']
        order_data = api_func('base', 'sale', order_id)
        whouse_recs = [r for r in warehouse_recds if r['savor_order_id']==order_id]
        if len(whouse_recs)>0:
            whouse_record = whouse_recs[0]

            if whouse_record['skus'] == unfld['skus'] and order_data['shipping_zip'] == whouse_record['shipping_zip']:
                new_fulfilled += 1
                # how to set it to fulfilled....
                post_data = {}
                post_data['update_date'] = whouse_record['ship_date']
                post_data['comment'] = 'auto-update from reconcile_warehouse'
                post_data['status'] = 'completed'
                post_data['shipper_id'] = api_func('inventory', 'shippingtype', whouse_record['shipping_type'])['shipper_id']
                post_data['tracking_number'] = whouse_record['tracking_number']
                post_data['fulfillment_id'] = unfld['id']
                post_fulfill_update(post_data)
            else:
                mismatched.append(unfld['order'])
                mismatch_fulfills += 1

    messages.info(request, 'Start fulfill: %d. New fulfilled: %d. New mismatches: %d' % (start_unfulfill, new_fulfilled, mismatch_fulfills))
    if len(mismatched) > 0:
        messages.error(request, '')
    return redirect('/inventory/')
