from fulfill.models import BatchRequest, Fulfillment
from fulfill.serializers import FulfillmentSerializer


def batched_fulfillments(qstring):
    return [x for x in list(set([x['fulfillments'] for x in BatchRequest.objects.all().values('fulfillments')])) if x]


def unbatched_fulfillments(qstring):
    batched_flmts = batched_fulfillments(qstring)
    
    qs = Fulfillment.objects \
                    .exclude(id__in=batched_flmts) \
                    .exclude(order__channel__label='AMZN') \
                    .filter(status='requested')

    qs = FulfillmentSerializer.setup_eager_loading(qs)

    data = FulfillmentSerializer(qs, many=True).data
    data = [f for f in data if f['ship_info'] != 'incomplete']
    return data
