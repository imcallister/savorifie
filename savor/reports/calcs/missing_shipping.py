from multipledispatch import dispatch

from django.db.models import Q

from fulfill.models import Fulfillment
from fulfill.serializers import FullFulfillmentSerializer2, FulfillmentSerializer


@dispatch(dict)
def missing_shipping(qstring):
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