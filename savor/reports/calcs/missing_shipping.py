from multipledispatch import dispatch

from django.db.models import Q

from fulfill.models import Fulfillment
from fulfill.serializers import FullFulfillmentSerializer2, FulfillmentSerializer


@dispatch(dict)
def missing_shipping(qstring):
    qs = Fulfillment.objects
    qs = qs.filter(status='requested')
    qs = qs.exclude(ship_type__label='BY_HAND')
    qs = qs.filter(Q(bill_to='') | Q(bill_to__isnull=True))

    qs = FulfillmentSerializer.setup_eager_loading(qs)
    flfmts = FulfillmentSerializer(qs, many=True).data

    for f in flfmts:
        f['skus'] = dict((l['inventory_item'], l['quantity']) for l in f['fulfill_lines'])
        del f['fulfill_lines']

    return flfmts
