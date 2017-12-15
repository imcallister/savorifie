from multipledispatch import dispatch
from django.db.models import Count, F

from fulfill.models import BatchRequest
from fulfill.serializers import SimpleBatchRequestSerializer, BatchRequestSerializer

"""
@dispatch(dict)
def batchrequest(qstring):
    qs = BatchRequest.objects \
                     .all()
    qs = SimpleBatchRequestSerializer.setup_eager_loading(qs)
    return SimpleBatchRequestSerializer(qs, many=True).data

"""

@dispatch(str, dict)
def batchrequest(id, qstring):
    qs = BatchRequest.objects \
                     .get(id=id)
    return BatchRequestSerializer(qs).data


@dispatch(dict)
def batchrequest(qstring):
    return BatchRequest.objects \
                       .all() \
                       .annotate(fulfillments_count=Count('fulfillments')) \
                       .annotate(location_name=F('location__label')) \
                       .values()