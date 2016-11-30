import datetime
from dateutil.parser import parse
from multipledispatch import dispatch
import itertools
import operator
from decimal import Decimal


from django.conf import settings
from django.db.models import Prefetch, Sum

import products.apiv1 as product_api
from .models import Sale, UnitSale, Channel, SalesTax, ChannelPayouts
from sales.serializers import FullSaleSerializer, SimpleSaleSerializer, \
    ShippingSaleSerializer, SaleFulfillmentSerializer, SalesTaxSerializer, \
    SaleProceedsSerializer, SalesTaxSerializer2, ChannelPayoutSerializer


@dispatch(str, dict)
def channel(channel_id, qstring):
    channel = Channel.objects.get(counterparty_id=channel_id)
    data = {'id': channel.id, 'counterparty_id': channel.counterparty.id}
    return data


# how to take str or unicode??
@dispatch(unicode, dict)
def channel(channel_id, qstring):
    channel = Channel.objects.get(counterparty_id=channel_id)
    data = {'id': channel.id, 'counterparty_id': channel.counterparty.id}
    return data


@dispatch(dict)
def channel(qstring):
    channels = Channel.objects.all()

    data = [{'id': channel.id, 'counterparty_id': channel.counterparty.id} for channel in channels]
    return data


def salestax(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())
    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()
    qs = SalesTax.objects.filter(sale__sale_date__gte=start_date,
                                 sale__sale_date__lte=end_date)

    serializer = SalesTaxSerializer
    qs = serializer.setup_eager_loading(qs)
    return list(serializer(qs, many=True).data)

def salestax2(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())
    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()
    qs = Sale.objects.filter(sale_date__gte=start_date,
                             sale_date__lte=end_date)

    serializer = SalesTaxSerializer2
    qs = serializer.setup_eager_loading(qs)
    return list(serializer(qs, many=True).data)

@dispatch(dict)
def sale(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())
    view_type = qstring.get('view', 'full')

    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()
    qs = Sale.objects.filter(sale_date__gte=start_date, sale_date__lte=end_date) \
                     .order_by('-sale_date')

    if view_type == 'simple':
        serializer = SimpleSaleSerializer
    elif view_type == 'shipping':
        serializer = ShippingSaleSerializer
    elif view_type == 'fulfillment':
        serializer = SaleFulfillmentSerializer
    else:
        serializer = FullSaleSerializer

    qs = serializer.setup_eager_loading(qs)
    return list(serializer(qs, many=True).data)


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


def sale_count(qstring):
    sku_count = UnitSale.objects.values('sku').annotate(cnt=Sum('quantity'))
    products = product_api.product({})

    item_count = {}
    for sku in sku_count:
        product_info = next((p for p in products if p['id'] == sku['sku']), None)
        for u in product_info['skuunit']:
            if u['inventory_item'] not in item_count:
                item_count[u['inventory_item']] = sku['cnt'] * u['quantity']
            else:
                item_count[u['inventory_item']] += sku['cnt'] * u['quantity']

    if qstring.get('chart'):
        sorted_data = sorted(item_count.items(), key=operator.itemgetter(1))
        chart_data = {}
        chart_data['x_vals'] = [x[0] for x in sorted_data]
        series_0 = {'name': 'Unit Sales'}
        series_0['data'] = [x[1] for x in sorted_data]
        chart_data['series'] = [series_0]
        return chart_data
    else:
        return item_count


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

def channel_payout_drilldown(payout_id, qstring):
    qs = ChannelPayouts.objects.get(id=payout_id).sales
    qs = SaleProceedsSerializer.setup_eager_loading(qs)
    return SaleProceedsSerializer(qs, many=True).data
    
def channel_payout_comp(channel_lbl, qstring):
    qs = ChannelPayouts.objects.filter(channel__counterparty_id=channel_lbl)
    qs = ChannelPayoutSerializer.setup_eager_loading(qs)
    output = ChannelPayoutSerializer(qs, many=True).data
    return [x for x in output if abs(x['diff']) > 1.0]
    

def unpaid_channel(channel_lbl, qstring):
    # find Shopify sales which are not in a channel payout batch
    paidout_sales = []
    for cpt in ChannelPayouts.objects.filter(channel__counterparty_id=channel_lbl):
        paidout_sales += [s.id for s in cpt.sales.all()]

    qs = Sale.objects.filter(channel__counterparty_id='SHOPIFY') \
                     .exclude(id__in=paidout_sales)
    qs = SaleProceedsSerializer.setup_eager_loading(qs)
    unpaid = list(SaleProceedsSerializer(qs, many=True).data)
    return [u for u in unpaid if u['proceeds'] != Decimal('0')]
