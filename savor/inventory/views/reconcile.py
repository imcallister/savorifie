from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from accountifie.common.api import api_func
from fulfill_requests import post_fulfill_update
from inventory.models import WarehouseFulfill
from inventory.serializers import WarehouseFulfillSerializer

def rec_zip(z1, z2):
    # deal with the dropped leading zero issue
    if len(z1)==4 and len(z2)==5 and z2[0]=='0':
        return (z1 == z2[1:])
    elif len(z2)==4 and len(z1)==5 and z1[0]=='0':
        return (z2 == z1[1:])
    else:
        return (z2==z1)

def whouseflf_from_fulfill(f_id):
    qs = WarehouseFulfill.objects \
                         .filter(fulfillment_id=f_id)
    qs = WarehouseFulfillSerializer.setup_eager_loading(qs)
    return WarehouseFulfillSerializer(qs, many=True).data


@login_required
def reconcile_warehouse(request):
    """
    For all fulfillments that are not completed
    look for matching warehouse record and do reconciliation

    reconcile:
    1: items match ...
    2: zip matches (?)
    3: shiping method matches
    4: store info in fulmfillment request and set status
    """

    incomplete = api_func('inventory', 'fulfillment', qstring={'status': 'requested'})
    incomplete += api_func('inventory', 'fulfillment', qstring={'status': 'partial'})
    incomplete += api_func('inventory', 'fulfillment', qstring={'status': 'mismatched'})

    start_incomplete = len(incomplete)
    new_completed = 0
    mismatch_fulfills = 0

    for unfld in incomplete:
        #fulfill_data = api_func('inventory', 'fulfillment', unfld['id'])
        wh_fulfill = whouseflf_from_fulfill(unfld['id'])

        if len(wh_fulfill) > 0:
            whouse_record = wh_fulfill[0]
            post_data = {}
            post_data['update_date'] = whouse_record['ship_date']
            post_data['comment'] = 'auto-update from reconcile_warehouse'
            print '-' * 20
            print 'working on'
            print whouse_record['shipping_type']
            print
            print whouse_record
            post_data['shipper_id'] = api_func('inventory', 'shippingtype',
                                               whouse_record['shipping_type'])['shipper']['id']
            post_data['tracking_number'] = whouse_record['tracking_number']
            post_data['fulfillment_id'] = unfld['id']

            whouse_rec_skus = dict((fl['inventory_item'], fl['quantity']) for fl in whouse_record['fulfill_lines'])
            if whouse_rec_skus == unfld['skus'] and \
               rec_zip(whouse_record['shipping_zip'],
                       unfld['order']['shipping_zip']):

                new_completed += 1
                post_data['status'] = 'completed'
            else:
                post_data['status'] = 'mismatched'
                mismatch_fulfills += 1

            post_fulfill_update(post_data)

    messages.info(request, 'Start unfulfilled: %d.\
                            New fulfilled: %d. \
                            New mismatches: %d'
                           % (start_incomplete, new_completed, mismatch_fulfills))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
