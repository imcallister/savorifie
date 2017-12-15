import itertools
from decimal import Decimal
import datetime

from django.db.models import Q

from .model_api import *
from ..models import ShippingCharge, Fulfillment
from ..serializers import ShippingChargeSerializer, FulfillmentSerializer
from accountifie.toolkit.utils import monthrange


def fulfill_no_shipcharge(qstring):
    with_shipcharge = [s['fulfillment_id'] for s in shippingcharge({}) \
                       if s['fulfillment_id']]
    SAVOR_UPS_ACCOUNT = '1V06Y4'
    CUTOFF = datetime.date(2016,7,1)
    qs = Fulfillment.objects \
                    .filter(request_date__gte=CUTOFF) \
                    .exclude(status='back-ordered') \
                    .exclude(warehouse__label='WRITEOFF') \
                    .exclude(id__in=with_shipcharge) \
                    .exclude(ship_type__label__in=['BY_HAND', 'FREIGHT', 'FEDEX_2DAY', 'FEDEX_GROUND', 'CUSTOMER_ACCOUNT']) \
                    .exclude(Q(ship_type__label__in=['UPS_GROUND', '100WEIGHTS']) & ~Q(bill_to__iexact=SAVOR_UPS_ACCOUNT))

    qs = FulfillmentSerializer.setup_eager_loading(qs)
    data = FulfillmentSerializer(qs, many=True).data
    def _get_row(row):
        out = {}
        out['fulfillment_id'] = str(row['id'])
        out['order'] = row['order']['label']
        out['request_date'] = row['request_date']
        out['shipping_name'] = row['order']['shipping_name']
        out['shipping_company'] = row['order']['shipping_company']
        try:
            out['ship_type'] = row.get('ship_type').get('label')
        except:
            out['ship_type'] = ''
        out['warehouse'] = row.get('warehouse')
        out['bill_to'] = row['bill_to']
        return out

    return [_get_row(f) for f in data]


def shipcharge_no_fulfill(qstring):
    qs = ShippingCharge.objects.filter(order_related=True) \
                               .filter(fulfillment=None)
    qs = ShippingChargeSerializer.setup_eager_loading(qs)
    data = ShippingChargeSerializer(qs, many=True).data
    return data
                       


def UPS_invoices(qstring):
    ship_charges = sorted(shippingcharge({'shipper': 'UPS'}), key=lambda x: x['invoice_number'])
    by_invoice = dict((k, list(v)) for k, v in itertools.groupby(ship_charges, lambda x: x['invoice_number']))

    def _get_line(k, v):
        return {'invoice_number': k,
                'charge': sum([Decimal(st['charge']) for st in v]),
                'last_date': max([st['ship_date'] for st in v])}
    return sorted([_get_line(k, v) for k, v in by_invoice.iteritems()],
                  key=lambda x: x['last_date'])


def IFS_monthly(qstring):
    ship_charges = sorted(shippingcharge({'shipper': 'IFS360'}), key=lambda x: x['invoice_number'])
    by_invoice = dict((k, list(v)) for k, v in itertools.groupby(ship_charges,
                                                                 lambda x: x['invoice_number']))

    drill_url = '/api/fulfill/shippingcharge?shipper=IFS360&invoice_number='

    def _drill_url(invoice_number, text):
        return '<a href=' + drill_url + invoice_number + '>' + text + '</a>';


    def _get_line(k, v):
        return {'invoice_number': k,
                'charge': sum([Decimal(st['charge']) for st in v]),
                'last_date': max([st['ship_date'] for st in v]),
                'drilldown': _drill_url(k, 'Details') if k else '-'}
    return sorted([_get_line(k, v) for k, v in by_invoice.iteritems()],
                  key=lambda x: x['last_date'])


def UPS_wrong_acct(qstring):
    flfls = fulfillment({'shipper': 'UPS'})

    def _filter(flfl):
        if f['bill_to']:
            return f['bill_to'].upper() != '1V06Y4'
        else:
            return True

    non_savor_flfls = [f['id'] for f in flfls if _filter(f)]
    qs = ShippingCharge.objects.filter(fulfillment__in=non_savor_flfls)
    qs = ShippingChargeSerializer.setup_eager_loading(qs)
    return list(ShippingChargeSerializer(qs, many=True).data)
