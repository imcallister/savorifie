import csv
from multipledispatch import dispatch
import itertools
import logging
import flatdict
import time

from django.db.models import Prefetch, Count, F

from accountifie.common.api import api_func
from inventory.models import *
from inventory.serializers import *
from base.models import *
from base.serializers import SimpleSaleSerializer, SaleFulfillmentSerializer

logger = logging.getLogger('default')

def batchrequest(qstring):
    batches = BatchRequest.objects \
                          .annotate(fulfillments_count=Count('fulfillments')) \
                          .annotate(location_label=F('location__label')) \
                          .all()  \
                          .values()
    return batches


def shipmentline(qstring):
    shpmts = ShipmentLine.objects \
                         .annotate(inventory_item_label=F('inventory_item__label')) \
                         .annotate(shipment_label=F('shipment__label')) \
                         .all() \
                         .values()

    return shpmts


def batched_fulfillments(qstring):
    qs = BatchRequest.objects.all()
    qs = BatchRequestSerializer.setup_eager_loading(qs)

    batched_flmts = [[x['id'] for x in b['fulfillments']]
                     for b in BatchRequestSerializer(qs, many=True).data]
    return list(itertools.chain(*batched_flmts))


def unbatched_fulfillments(qstring):
    batched_flmts = batched_fulfillments(qstring)
    qs = Fulfillment.objects.exclude(id__in=batched_flmts)
    qs = FulfillmentSerializer.setup_eager_loading(qs)

    return [{'label': f['order']['label'], 'id': f['id'], 'warehouse': f['warehouse']} \
            for f in FulfillmentSerializer(qs, many=True).data]


@dispatch(dict)
def warehousefulfill(qstring):
    qs = WarehouseFulfill.objects.all()

    qs = WarehouseFulfillSerializer.setup_eager_loading(qs)
    wh_flmts = WarehouseFulfillSerializer(qs, many=True).data
    for f in wh_flmts:
        f['skus'] = dict((l['inventory_item'], l['quantity']) for l in f['fulfill_lines'])
        del f['fulfill_lines']

    return wh_flmts


@dispatch(str, dict)
def warehousefulfill(warehouse_pack_id, qstring):    
    qs = WarehouseFulfill.objects \
                         .filter(warehouse_pack_id=warehouse_pack_id) \
                         .first()
    whf = WarehouseFulfillSerializer(qs).data
    whf['skus'] = dict((l['inventory_item'], l['quantity']) for l in whf['fulfill_lines'])
    del whf['fulfill_lines']

    return whf


def _missing_shipping(rec):
    if rec['ship_type'] and rec['bill_to'] != '':
            return False
    elif rec['ship_type'] == 'BY_HAND':
            return False
    else:
        return True


@dispatch(dict)
def fulfillment(qstring):
    start = time.time()
    qs = Fulfillment.objects.all()
    qs = FulfillmentSerializer.setup_eager_loading(qs)
    
    if qstring.get('warehouse'):
        qs = qs.filter(warehouse__label=qstring.get('warehouse'))

    if 'status' in qstring:
        qs = qs.filter(status__in=qstring['status'].split(','))
    
    flfmts = FulfillmentSerializer(qs, many=True).data
    if qstring.get('missing_shipping', '').lower() == 'true':
        flfmts = [r for r in flfmts if _missing_shipping(r)]
    for f in flfmts:
        f['skus'] = dict((l['inventory_item'], l['quantity']) for l in f['fulfill_lines'])
        del f['fulfill_lines']
    return flfmts


@dispatch(str, dict)
def fulfillment(id, qstring):
    qs = Fulfillment.objects.filter(id=id).first()
    flfmt = FulfillmentSerializer(qs).data
    flfmt['skus'] = dict((l['inventory_item'], l['quantity']) for l in flfmt['fulfill_lines'])
    del flfmt['fulfill_lines']
    return flfmt


def requested(qstring):
    unfulfilled = api_func('inventory',
                           'fulfillment',
                           qstring={'status': 'requested,partial'})

    for unf in unfulfilled:
        unf['items'] =','.join(['%s %s' % (v, k) for k,v in unf['skus'].iteritems()])
        del unf['skus']

    data = [dict((str(k), str(v)) for k, v in flatdict.FlatDict(f).iteritems()) for f in unfulfilled]
    return data


def fulfilled(qstring):
    fulfilled = api_func('inventory',
                         'fulfillment',
                         qstring={'status': 'completed'})

    for ful in fulfilled:
        ful['items'] =','.join(['%s %s' % (v, k) for k,v in ful['skus'].iteritems()])
        del ful['skus']

    data = [dict((str(k), str(v)) for k, v in flatdict.FlatDict(f).iteritems()) for f in fulfilled]
    return data

def backordered(qstring):
    """
    find all sale objects for which fulfillment is backordered
    """
    qs = Fulfillment.objects.filter(status='back-ordered')
    qs = FulfillmentSerializer.setup_eager_loading(qs)
    return FulfillmentSerializer(qs, many=True).data


@dispatch(dict)
def unfulfilled(qstring):
    """
    find all sale objects for which there is no fulfillment record
    """
    sales_qs = Sale.objects \
                   .prefetch_related('unit_sale__sku__skuunit__inventory_item') \
                   .prefetch_related('fulfillments__fulfill_lines__inventory_item') \
                   .all()

    incomplete = [s.id for s in sales_qs if s.unfulfilled_items]
    
    qs = Sale.objects.filter(id__in=incomplete)
    qs = SaleFulfillmentSerializer.setup_eager_loading(qs)
    return SaleFulfillmentSerializer(qs, many=True).data


@dispatch(str, dict)
def unfulfilled(id, qstring):
    """
    find all sale objects for which there is no fulfillment record
    """
    qs = Sale.objects.get(id=id)
    return SaleFulfillmentSerializer(qs).data
