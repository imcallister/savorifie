from fulfill.models import Fulfillment
from fulfill.serializers import FulfillmentSerializer


def backordered(qstring):
    """
    find all sale objects for which fulfillment is backordered
    """
    qs = Fulfillment.objects.filter(status='back-ordered')
    qs = FulfillmentSerializer.setup_eager_loading(qs)
    return FulfillmentSerializer(qs, many=True).data
