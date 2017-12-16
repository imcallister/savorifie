import time
import datetime
from dateutil.parser import parse
from multipledispatch import dispatch
import itertools
import operator
from decimal import Decimal


from django.conf import settings
from django.db.models import Prefetch, Sum, F, DecimalField, Max
from django.db.models.functions import Coalesce
from django.utils.safestring import mark_safe

import products.apiv1 as product_api
from fulfill.models import FulfillLine
from products.models import SKUUnit

from sales.models import Sale, UnitSale, Channel, Payout, PayoutLine
from sales.serializers import FullSaleSerializer, SimpleSaleSerializer, \
    ShippingSaleSerializer, SaleFulfillmentSerializer, SaleProceedsSerializer,\
    PayoutSerializer, SaleIDSerializer, SaleGrossProceedsSerializer, \
    SaleProceedsAdjustmentSerializer, SalePayoutsSerializer, SalesTaxSerializer3, \
    SimpleSaleSerializer2

def external_ids(qstring):
    qs = Sale.objects
    filter_string = qstring.get('filter', None)
    if filter_string:
        qs = qs.filter(external_channel_id__icontains=filter_string)
    return list(SaleIDSerializer(qs, many=True).data)


def sales_loaded_thru(channel_lbl, qstring):
    latest = Sale.objects.filter(channel__label=channel_lbl) \
                      .aggregate(Max('sale_date'))
    return latest['sale_date__max']

def _get_lines(skus, us):
    return [{'inventory_item': s['inventory_item'],
             'sale_id': us['sale_id'],
             'quantity__sum': us['quantity__sum'] * s['quantity']} for s in skus.get(us['sku_id'], [])]

@dispatch(dict)
def sales_list(q):
    start_date = q.get('from_date', settings.DATE_EARLY)
    end_date = q.get('to_date', datetime.datetime.now().date())

    usls = sorted(UnitSale.objects.values('sale_id', 'sku__label').annotate(Sum('quantity')),
                  key=lambda x: x['sale_id'])
    
    def _get_str(row):
        return '%s %s' % (row['quantity__sum'], row['sku__label'])

    items = dict((k, ','.join([_get_str(r) for r in list(g)])) for k, g in itertools.groupby(usls, key=lambda x: x['sale_id']))

    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()
    qs = Sale.objects.filter(sale_date__gte=start_date, sale_date__lte=end_date) \
                     .order_by('-sale_date')

    qs = SimpleSaleSerializer2.setup_eager_loading(qs)
    data = SimpleSaleSerializer2(qs, many=True).data

    for d in data:
        d['drilldown'] = mark_safe('<a href="/order/drilldown/%s">%s</a>' % (d['id'], d['label']))
        d['items_string'] = items.get(d['id'], '')
    return data


@dispatch(dict)
def unfulfilled(qstring):
    sales_qs = Sale.objects \
                   .prefetch_related('unit_sale__sku__skuunit__inventory_item') \
                   .prefetch_related('fulfillments__fulfill_lines__inventory_item')

    incomplete = [s.id for s in sales_qs if s.unfulfilled_items]
    
    qs = Sale.objects.filter(id__in=incomplete)
    qs = SaleFulfillmentSerializer.setup_eager_loading(qs)
    return SaleFulfillmentSerializer(qs, many=True).data


@dispatch(str, dict)
def unfulfilled(id, qstring):
    qs = Sale.objects.get(id=id)
    return SaleFulfillmentSerializer(qs).data

@dispatch(dict)
def sale(qstring):
    start = time.time()
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())
    view_type = qstring.get('view', 'full')
    paid_thru = qstring.get('paid_thru')

    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()
    qs = Sale.objects.filter(sale_date__gte=start_date, sale_date__lte=end_date) \
                     .order_by('-sale_date')

    if paid_thru:
        qs = qs.filter(paid_thru_id=paid_thru)
    
    if view_type == 'simple':
        serializer = SimpleSaleSerializer
    elif view_type == 'simple2':
        serializer = SimpleSaleSerializer2
    elif view_type == 'shipping':
        serializer = ShippingSaleSerializer
    elif view_type == 'fulfillment':
        serializer = SaleFulfillmentSerializer
    elif view_type == 'proceeds':
        serializer = SaleProceedsSerializer
    elif view_type == 'grossproceeds':
        qs = qs.annotate(gross_proceeds=Coalesce(Sum(F('unit_sale__quantity') * F('unit_sale__unit_price'), output_field=DecimalField()),
                                                 Decimal('0')))
        serializer = SaleGrossProceedsSerializer
    elif view_type == 'proceedsadjustments':
        qs = qs.annotate(total_adjustments=Coalesce(Sum('proceedsadjustment_sale__amount', output_field=DecimalField()),
                                                    Decimal('0')))
        serializer = SaleProceedsAdjustmentSerializer
    elif view_type == 'payouts':
        qs = qs.annotate(total_payout=Coalesce(Sum('payoutline_sale__amount', output_field=DecimalField()),
                                               Decimal('0')))
        serializer = SalePayoutsSerializer
    elif view_type == 'salestax':
        qs = qs.annotate(total_salestax=Coalesce(Sum('sales_tax__tax', output_field=DecimalField()),
                                               Decimal('0')))
        serializer = SalesTaxSerializer3
    else:
        serializer = FullSaleSerializer
    qs = serializer.setup_eager_loading(qs)
    data = list(serializer(qs, many=True).data)
    return data


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
    qs = Sale.objects.filter(customer_code='unknown')
    qs = SimpleSaleSerializer.setup_eager_loading(qs)
    return SimpleSaleSerializer(qs, many=True).data


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
    
def unpaid_sales(channel_lbl, qstring):
    """
    For sales in a given channel aggregate all the payoutlines
    and report on those where aggregated payouts do not match
    the total receivable on the order
    """
    pls = PayoutLine.objects.filter(payout__channel__counterparty_id=channel_lbl) \
                            .values('sale_id') \
                            .annotate(total=Sum('amount'))
    
    payout_lines = dict((p['sale_id'], p['total']) for p in pls)
    
    sale_ids = [t['sale_id'] for t in pls]
    qs = Sale.objects.filter(id__in=sale_ids)
    qs = SaleProceedsSerializer.setup_eager_loading(qs)
    proceeds = SaleProceedsSerializer(qs, many=True).data

    cols = ['label', 'sale_date', 'paid_thru', 'shipping_name', 'proceeds', 'items_string']

    def _get_row(raw):
        row = dict((k, raw.get(k)) for k in cols)
        if not row['proceeds']:
            row['proceeds'] = Decimal('0')

        row['received'] = payout_lines.get(raw['id'], Decimal('0'))
        row['diff'] = row['proceeds'] - row['received']
        return row

    output = [_get_row(r) for r in proceeds]
    output = [r for r in output if abs(r['diff']) > Decimal('1')]

    return output




def unpaid_channel(channel_lbl, qstring):
    # find Shopify sales which are not in a channel payout batch
    paidout_sales = [x['sale_id'] for x in PayoutLine.objects.filter(payout__channel__label=channel_lbl).values('sale_id')]
    qs = Sale.objects.filter(channel__label=channel_lbl) \
                     .exclude(id__in=paidout_sales)
    qs = SaleProceedsSerializer.setup_eager_loading(qs)
    unpaid = list(SaleProceedsSerializer(qs, many=True).data)
    return [u for u in unpaid if u['proceeds'] != Decimal('0')]
