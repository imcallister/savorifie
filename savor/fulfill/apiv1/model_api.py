from multipledispatch import dispatch
import logging
import flatdict
import time

from django.db.models import Count, Q

from ..models import *
from ..serializers import *


logger = logging.getLogger('default')


@dispatch(dict)
def shippingcharge(qstring):

    qs = ShippingCharge.objects \
                       .all()

    if qstring.get('shipper'):
        qs = qs.filter(shipper__company__id=qstring.get('shipper'))

    if qstring.get('fulfill'):
        qs = qs.filter(fulfillment_id=qstring.get('fulfill'))

    if qstring.get('invoice_number'):
        qs = qs.filter(invoice_number=qstring.get('invoice_number'))        

    qs = ShippingChargeSerializer.setup_eager_loading(qs)
    return list(ShippingChargeSerializer(qs, many=True).data)


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


@dispatch(dict)
def warehousefulfill(qstring):
    qs = WarehouseFulfill.objects.all()

    if qstring.get('fulfill'):
        qs = qs.filter(fulfillment_id=qstring.get('fulfill'))

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
    view_type = qstring.get('view', 'standard')
    if type(view_type) == list:
        view_type = view_type[0]

    qs = Fulfillment.objects.all()

    if view_type == 'full':
        serializer = FullFulfillmentSerializer2
    else:
        serializer = FulfillmentSerializer
    
    qs = serializer.setup_eager_loading(qs)

    if qstring.get('warehouse'):
        qs = qs.filter(warehouse__label=qstring.get('warehouse'))

    if qstring.get('shipper'):
        qs = qs.filter(ship_type__shipper__company__id=qstring.get('shipper'))

    if 'status' in qstring:
        qs = qs.filter(status__in=qstring['status'].split(','))

    if qstring.get('missing_shipping', '').lower() == 'true':
        qs = qs.exclude(ship_type__label='BY_HAND')
        qs = qs.filter(Q(bill_to='') | Q(bill_to__isnull=True))


    flfmts = serializer(qs, many=True).data

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
        serializer = FullFulfillmentSerializer2
    else:
        serializer = FulfillmentSerializer
    
    flfmt = serializer(qs).data
    flfmt['skus'] = dict((l['inventory_item'], l['quantity']) for l in flfmt['fulfill_lines'])
    del flfmt['fulfill_lines']
    return flfmt


def no_warehouse_record(qstring):
    """
    Find fulfillments which have been batched but have 
    no associated warehouse fulfillment record
    """
    pre_qs = Fulfillment.objects.exclude(ship_type__label='BY_HAND')

    if qstring.get('warehouse'):
        pre_qs = pre_qs.filter(warehouse__label=qstring.get('warehouse'))

    objs = pre_qs.annotate(num_whf=Count('warehousefulfill')) \
                  .annotate(batched=Count('batchrequest')) \
                  .values('num_whf', 'batched', 'id')

    nwr = [f['id'] for f in objs if  f['num_whf']==0]
    
    qs = Fulfillment.objects.filter(id__in=nwr)
    qs = FulfillmentSerializer.setup_eager_loading(qs)
    flfmts = FulfillmentSerializer(qs, many=True).data
    if qstring.get('missing_shipping', '').lower() == 'true':
        flfmts = [r for r in flfmts if r['ship_info'] == 'incomplete']
    for f in flfmts:
        f['skus'] = dict((l['inventory_item'], l['quantity']) for l in f['fulfill_lines'])
        del f['fulfill_lines']

    data = [dict((str(k), str(v)) for k, v in flatdict.FlatDict(f).iteritems()) for f in flfmts]
    return data


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


"""
@dispatch(dict)
def unfulfilled(qstring):
    sales_qs = Sale.objects \
                   .prefetch_related('unit_sale__sku__skuunit__inventory_item') \
                   .prefetch_related('fulfillments__fulfill_lines__inventory_item')

    incomplete = [s.id for s in sales_qs if s.unfulfilled_items]
    
    qs = Sale.objects.filter(id__in=incomplete)
    qs = SaleFulfillmentSerializer.setup_eager_loading(qs)
    return SaleFulfillmentSerializer(qs, many=True).data


@dispatch(str, dict)
def unfulfilled(id, qstring):
    qs = Sale.objects.get(id=id)
    return SaleFulfillmentSerializer(qs).data
"""