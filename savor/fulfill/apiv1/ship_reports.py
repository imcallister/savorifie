import itertools
from decimal import Decimal

from .model_api import *
from fulfill.models import ShippingCharge
from fulfill.serializers import ShippingChargeSerializer

def UPS_invoices(qstring):
    ship_charges = sorted(shippingcharge({}), key=lambda x: x['invoice_number'])
    by_invoice = dict((k, list(v)) for k, v in itertools.groupby(ship_charges, lambda x: x['invoice_number']))

    def _get_line(k, v):
        return {'invoice_number': k,
                'charge': sum([Decimal(st['charge']) for st in v]),
                'last_date': max([st['ship_date'] for st in v])}
    return sorted([_get_line(k, v) for k, v in by_invoice.iteritems()],
                  key=lambda x: x['last_date'])


def UPS_wrong_acct(qstring):
    flfls = fulfillment({})

    def _filter(flfl):
        if f['bill_to']:
            return f['bill_to'].upper() != '1V06Y4'
        else:
            return True

    non_savor_flfls = [f['id'] for f in flfls if _filter(f)]
    qs = ShippingCharge.objects.filter(fulfillment__in=non_savor_flfls)
    qs = ShippingChargeSerializer.setup_eager_loading(qs)
    return list(ShippingChargeSerializer(qs, many=True).data)
