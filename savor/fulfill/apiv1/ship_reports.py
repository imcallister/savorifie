import itertools
from decimal import Decimal

from .model_api import *


def UPS_invoices(qstring):
    ship_charges = sorted(shippingcharge({}), key=lambda x: x['invoice_number'])
    by_invoice = dict((k, list(v)) for k, v in itertools.groupby(ship_charges, lambda x: x['invoice_number']))

    def _get_line(k, v):
        return {'invoice_number': k,
                'charge': sum([Decimal(st['charge']) for st in v]),
                'last_date': max([st['ship_date'] for st in v])}
    return sorted([_get_line(k, v) for k, v in by_invoice.iteritems()],
                  key=lambda x: x['last_date'])
