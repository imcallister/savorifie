import datetime
from dateutil.parser import parse
from multipledispatch import dispatch
import itertools
import operator


from django.conf import settings
from django.db.models import Prefetch

import products.apiv1 as product_api
from savor.base.models import Sale, UnitSale, Channel
from base.serializers import FullSaleSerializer, SimpleSaleSerializer, \
    ShippingSaleSerializer, SaleFulfillmentSerializer


@dispatch(dict)
def sale(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())
    view_type = qstring.get('view', 'full')

    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()
    qs = Sale.objects.filter(sale_date__gte=start_date, sale_date__lte=end_date)

    if view_type == 'simple':
        serializer = SimpleSaleSerializer
    elif view_type == 'shipping':
        serializer = ShippingSaleSerializer
    elif view_type == 'fulfillment':
        serializer = SaleFulfillmentSerializer
    else:
        serializer = FullSaleSerializer

    qs = serializer.setup_eager_loading(qs)
    return serializer(qs, many=True).data


@dispatch(str, dict)
def sale(id, qstring):
    view_type = qstring.get('view', 'full')
    if type(view_type) == list:
        view_type = view_type[0]

    qs = Sale.objects.filter(id=id).first()

    if view_type == 'simple':
        serializer = SimpleSaleSerializer
    elif view_type == 'shipping':
        serializer = ShippingSaleSerializer
    elif view_type == 'fulfillment':
        serializer = SaleFulfillmentSerializer
    elif view_type == 'drilldown':
        serializer = SaleDrilldownSerializer
    else:
        serializer = FullSaleSerializer

    return serializer(qs).data


@dispatch(unicode, dict)
def sale(id, qstring):
    qs = Sale.objects.filter(id=id).first()
    return FullSaleSerializer(qs).data


def sales_by_month(qstring):
    all_sales = sorted(sale({'view': 'full'}), key=lambda x: parse(x['sale_date']))
    output = qstring.get('output', 'raw')

    def group_key(o):
        dt = parse(o['sale_date'])
        return (dt.year, dt.month)

    def agg(o):
        return sum([u['quantity'] for u in o['unit_sale']])

    def fmt_month(m):
        return datetime.date(m[0], m[1], 1).strftime('%b-%y')

    grouped = itertools.groupby(all_sales, key=group_key)
    if output == 'raw':
        return dict((fmt_month(k), sum([agg(o) for o in v])) for k, v in grouped)
    elif output == 'chart':
        data = dict((k, sum([agg(o) for o in v])) for k, v in grouped)
        sorted_dates = sorted(data.keys(), key=lambda x: x[0]*12 + x[1])

        chart_data = {}
        chart_data['chart_data'] = {}
        chart_data['chart_data']['x_points'] = [fmt_month(d) for d in sorted_dates]
        chart_data['chart_data']['values'] = []
        chart_data['chart_data']['values'].append([data.get(x, 0) for x in sorted_dates])
        chart_data['chart_data']['seriesTypes'] = ['bar']
        return chart_data
    else:
        return None


def incomplete_sales_count(qstring):
    return Sale.objects.filter(customer_code='unknown').count()

def sales_by_counterparty(qstring):
    all_sales = sorted(sale({'view': 'full'}), key=lambda x: x['customer_code'])
    output = qstring.get('output', 'raw')

    def agg(o):
        return sum([u['quantity'] for u in o['unit_sale']])

    grouped = itertools.groupby(all_sales, key=lambda x: x['customer_code'])
    if output == 'raw':
        return dict((k, sum([agg(o) for o in v])) for k, v in grouped)
    elif output == 'chart':
        data = dict((k, sum([agg(o) for o in v])) for k, v in grouped)
        sorted_data = sorted(data.items(), key=operator.itemgetter(1))
        sorted_data = [x for x in sorted_data if x[1] >= 5]
        chart_data = {}
        chart_data['chart_data'] = {}
        chart_data['chart_data']['x_points'] = [x[0] for x in sorted_data]
        chart_data['chart_data']['values'] = []
        chart_data['chart_data']['values'].append([x[1] for x in sorted_data])
        chart_data['chart_data']['seriesTypes'] = ['bar']
        return chart_data


def sales_by_channel(qstring):
    all_sales = sorted(sale({'view': 'full'}), key=lambda x: x['channel'])
    output = qstring.get('output', 'raw')

    def agg(o):
        return sum([u['quantity'] for u in o['unit_sale']])

    grouped = itertools.groupby(all_sales, key=lambda x: x['channel'])
    if output == 'raw':
        return dict((k, sum([agg(o) for o in v])) for k, v in grouped)
    elif output == 'chart':
        data = dict((k, sum([agg(o) for o in v])) for k, v in grouped)
        sorted_data = sorted(data.items(), key=operator.itemgetter(1))

        chart_data = {}
        chart_data['chart_data'] = {}
        chart_data['chart_data']['x_points'] = [x[0] for x in sorted_data]
        chart_data['chart_data']['values'] = []
        chart_data['chart_data']['values'].append([x[1] for x in sorted_data])
        chart_data['chart_data']['seriesTypes'] = ['bar']
        return chart_data


def missing_cps(qstring):
    qs = Sale.objects.filter(customer_code__id='unknown')
    qs = SimpleSaleSerializer.setup_eager_loading(qs)
    return SimpleSaleSerializer(qs).data


def channel_counts(qstring):
    channels = Channel.objects.all()
    return dict((str(channel), Sale.objects.filter(channel=channel).count()) for channel in channels)


def sales_counts(qstring):
    all_skus = product_api.inventoryitem({})
    all_sales = UnitSale.objects.all() \
                                .prefetch_related(Prefetch('sku__skuunit__inventory_item'))

    sales_counts = dict((k['label'],0) for k in all_skus)

    for u_sale in all_sales:
        u_sale_counts = u_sale.inventory_items()
        for sku in u_sale_counts:
            sales_counts[sku] += u_sale_counts[sku]

    return sales_counts
