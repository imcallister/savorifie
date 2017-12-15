import time
import itertools
import datetime

from django.utils.safestring import mark_safe
from django.db.models import Sum
from django.conf import settings

from sales.models import Sale, UnitSale
from sales.serializers import SimpleSaleSerializer2
from fulfill.models import FulfillLine
from products.models import SKUUnit


def _get_lines(skus, us):
    return [{'inventory_item': s['inventory_item'],
             'sale_id': us['sale_id'],
             'quantity__sum': us['quantity__sum'] * s['quantity']} for s in skus.get(us['sku_id'], [])]


def sales_list(q):
    start = time.time()
    start_date = q.get('from_date', settings.DATE_EARLY)
    end_date = q.get('to_date', datetime.datetime.now().date())

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

    return data
