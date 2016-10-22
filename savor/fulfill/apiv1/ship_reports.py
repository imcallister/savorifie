import itertools
from decimal import Decimal
import datetime
import calendar
from dateutil.parser import parse

from django.db.models import Q

from .model_api import *
from fulfill.models import ShippingCharge, Fulfillment
from fulfill.serializers import ShippingChargeSerializer, FulfillmentSerializer
from accountifie.toolkit.utils import monthrange

def fulfill_no_shipcharge(qstring):
    with_shipcharge = [s['fulfillment_id'] for s in shippingcharge({}) \
                       if s['fulfillment_id']]
    
    SAVOR_UPS_ACCOUNT = '1V06Y4'
    CUTOFF = datetime.date(2016,7,1)
    qs = Fulfillment.objects \
                    .filter(request_date__gte=CUTOFF) \
                    .exclude(status='back-ordered') \
                    .exclude(id__in=with_shipcharge) \
                    .exclude(ship_type__label__in=['BY_HAND', 'FREIGHT', 'FEDEX_2DAY', 'FEDEX_GROUND']) \
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
    # IFS charges ...   aim is to reconcile to their statements
    #  they report on monthly basis
    # so generate "statements" based on calendar months
    # how to calculate? .... do it by shipping carge filtered on shipper==IFS360

    ship_charges = sorted(shippingcharge({'shipper': 'IFS360'}), key=lambda x: x['ship_date'])

    def _get_month(dt):
        dt = parse(dt).date()
        return (dt.month, dt.year)
    
    by_invoice = dict((k, list(v)) for k, v in itertools.groupby(ship_charges,
                                                                 lambda x: _get_month(x['ship_date'])))

    def _get_line(k, v):
        return {'statement_month': '%s %s' % (calendar.month_name[k[0]], k[1]),
                'charge': sum([Decimal(st['charge']) for st in v]),
                'last_date': max([st['ship_date'] for st in v])}
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
