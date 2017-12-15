import time
import itertools
from django.db.models import Sum

from sales.models import Sale, UnitSale
from sales.serializers import SaleFulfillmentSerializer, SimpleSaleSerializer
from fulfill.models import FulfillLine
from products.models import SKUUnit


def unfulfilled(qstring):
    """
    find all sale objects for which there is no fulfillment record
    """
    sales_qs = Sale.objects \
                   .exclude(channel__label='AMZN') \
                   .prefetch_related('unit_sale__sku__skuunit__inventory_item') \
                   .prefetch_related('fulfillments__fulfill_lines__inventory_item')

    incomplete = [s.id for s in sales_qs if s.unfulfilled_items]

    qs = Sale.objects.filter(id__in=incomplete)
    qs = SaleFulfillmentSerializer.setup_eager_loading(qs)
    return SaleFulfillmentSerializer(qs, many=True).data


def report2(q):
    """
    find all sale objects for which there is no fulfillment record
    """
    start = time.time()
    sales_qs = Sale.objects \
                   .exclude(channel__label='AMZN') \
                   .prefetch_related('unit_sale__sku__skuunit__inventory_item') \
                   .prefetch_related('fulfillments__fulfill_lines__inventory_item')
    incomplete = [s.id for s in sales_qs if s.unfulfilled_items]

    qs = Sale.objects.filter(id__in=incomplete)
    qs = SaleFulfillmentSerializer.setup_eager_loading(qs)
    data = SaleFulfillmentSerializer(qs, many=True).data

    meta = {}
    meta['title'] = 'Unfulfilled Items'
    meta['columns'] = [{'key': 'external_channel_id', 'label': 'Order #', 'alignRight': True, 'sortable': True, 'filter': True},
                       {'key': 'customer_code', 'label': 'Customer', 'alignRight': True, 'fmtr': '0,0', 'sortable': True, 'filter': True},
                       {'key': 'items_string', 'label': 'Items Ordered', 'alignRight': True, 'sortable': True},
                       {'key': 'unfulfilled_string', 'label': 'Items Unfulfilled', 'alignRight': True, 'sortable': True},
                       ]
    print(time.time() - start)
    return {'meta': meta, 'data': data}


def _get_lines(skus, us):
    return [{'inventory_item': s['inventory_item'],
             'sale_id': us['sale_id'],
             'quantity__sum': us['quantity__sum'] * s['quantity']} for s in skus.get(us['sku_id'], [])]


def report(q):
    start = time.time()
    fls = FulfillLine.objects \
                     .values('fulfillment__order_id', 'inventory_item') \
                     .annotate(Sum('quantity'))
    usls = UnitSale.objects.values('sale_id', 'sku_id').annotate(Sum('quantity'))
    
    skus = SKUUnit.objects.all().values('inventory_item', 'quantity', 'sku_id')
    skus = sorted(skus, key=lambda sku: sku['sku_id'])
    sku_map = dict((k, list(g)) for k, g in itertools.groupby(skus, key=lambda sku:sku['sku_id']))

    usls_expd = sum([_get_lines(sku_map, us) for us in usls], [])

    us_d = dict(((f['sale_id'], f['inventory_item']), f['quantity__sum']) for f in usls_expd)
    fl_d = dict(((f['fulfillment__order_id'], f['inventory_item']), f['quantity__sum']) for f in fls)

    all_ids = list(set(list(us_d.keys()) + list(fl_d.keys())))
    diff = dict((i, us_d.get(i, 0) - fl_d.get(i, 0)) for i in all_ids)
    unfulfilled = [{'sale_id': k[0], 'inventory_item': k[1], 'unfulfilled': v} for k, v in diff.items() if v != 0]
    
    qs = Sale.objects.filter(id__in=set(i['sale_id'] for i in unfulfilled))
    qs = SaleFulfillmentSerializer.setup_eager_loading(qs)
    return SaleFulfillmentSerializer(qs, many=True).data

