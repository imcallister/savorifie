import csv
from multipledispatch import dispatch
import itertools
import logging
import flatdict
import time

from django.db.models import Prefetch, Count, F

from .models import *
from .serializers import *
from sales.models import *
from sales.serializers import SimpleSaleSerializer, SaleFulfillmentSerializer

logger = logging.getLogger('default')

@dispatch(dict)
def batchrequest(qstring):
    qs = BatchRequest.objects \
                     .all()
    qs = SimpleBatchRequestSerializer.setup_eager_loading(qs)
    return SimpleBatchRequestSerializer(qs, many=True).data


@dispatch(str, dict)
def batchrequest(id, qstring):
    qs = BatchRequest.objects \
                     .get(id=id)
    return BatchRequestSerializer(qs).data


@dispatch(str, dict)
def fulfillment_batch(id, qstring):
    batch_id = BatchRequest.objects \
                           .filter(fulfillments__in=[id]) \
                           .first() \
                           .id
    return {'batch_id': batch_id}

def batched_fulfillments(qstring):
    qs = BatchRequest.objects.all()
    qs = BatchRequestSerializer.setup_eager_loading(qs)

    batched_flmts = [[x['id'] for x in b['fulfillments']]
                     for b in BatchRequestSerializer(qs, many=True).data]
    return list(itertools.chain(*batched_flmts))


def unbatched_fulfillments(qstring):
    batched_flmts = batched_fulfillments(qstring)
    missing_shipping = [f['id'] for f in fulfillment({'missing_shipping': 'true',
                                                      'status': 'requested'})]

    qs = Fulfillment.objects \
                    .exclude(id__in=batched_flmts) \
                    .exclude(id__in=missing_shipping) \
                    .filter(status='requested')
    qs = FulfillmentSerializer.setup_eager_loading(qs)

    return FulfillmentSerializer(qs, many=True).data


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


@dispatch(dict)
def fulfillment(qstring):
    qs = Fulfillment.objects.all()
    qs = FulfillmentSerializer.setup_eager_loading(qs)

    if qstring.get('warehouse'):
        qs = qs.filter(warehouse__label=qstring.get('warehouse'))

    if 'status' in qstring:
        qs = qs.filter(status__in=qstring['status'].split(','))

    flfmts = FulfillmentSerializer(qs, many=True).data
    if qstring.get('missing_shipping', '').lower() == 'true':
        flfmts = [r for r in flfmts if r['ship_info'] == 'incomplete']
    for f in flfmts:
        f['skus'] = dict((l['inventory_item'], l['quantity']) for l in f['fulfill_lines'])
        del f['fulfill_lines']
    return flfmts


@dispatch(str, dict)
def fulfillment(id, qstring):
    view_type = qstring.get('view', 'standard')
    if type(view_type) == list:
        view_type = view_type[0]

    qs = Fulfillment.objects.filter(id=id).first()
    
    if view_type == 'full':
        serializer = FullFulfillmentSerializer
    else:
        serializer = FulfillmentSerializer
    
    flfmt = serializer(qs).data
    flfmt['skus'] = dict((l['inventory_item'], l['quantity']) for l in flfmt['fulfill_lines'])
    del flfmt['fulfill_lines']
    return flfmt


def requested(qstring):
    qs = qstring.copy()
    qs['status'] = 'requested,partial'
    unfulfilled = fulfillment(qs)

    # filter out unbatched
    unbatched = [f['id'] for f in unbatched_fulfillments({})]
    unfulfilled = [f for f in unfulfilled if f['id'] not in unbatched]
    for unf in unfulfilled:
        unf['items'] =','.join(['%s %s' % (v, k) for k,v in unf['skus'].iteritems()])
        del unf['skus']

    data = [dict((str(k), str(v)) for k, v in flatdict.FlatDict(f).iteritems()) for f in unfulfilled]
    return data


def fulfilled(qstring):
    fulfilled = fulfillment(qstring={'status': 'completed'})
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
