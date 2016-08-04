import datetime
from multipledispatch import dispatch

from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models import Prefetch

from accountifie.common.api import api_func
from savor.base.models import Sale, UnitSale, Channel
from base.serializers import *


@dispatch(dict)
def sale(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())

    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()
    qs = Sale.objects.filter(sale_date__gte=start_date, sale_date__lte=end_date)
    qs = FullSaleSerializer.setup_eager_loading(qs)
    return FullSaleSerializer(qs, many=True).data


@dispatch(str, dict)
def sale(id, qstring):
    qs = Sale.objects.filter(id=id).first()
    return FullSaleSerializer(qs).data


@dispatch(unicode, dict)
def sale(id, qstring):
    qs = Sale.objects.filter(id=id).first()
    return FullSaleSerializer(qs).data


def summary_sales_stats(qstring):
    unit_sales_info = unit_sales(qstring)
    inventory_items = api_func('inventory', 'inventoryitem')
    for item in inventory_items:
        item['sold'] = len([x for x in unit_sales_info if x['inventory item']==item['label']])

    stats = dict((item['label'], item['sold']) for item in inventory_items)
    return stats


def missing_cps(qstring):
    qs = Sale.objects.filter(customer_code__id='unknown')
    qs = SimpleSaleSerializer.setup_eager_loading(qs)
    return SimpleSaleSerializer(qs).data


def channel_counts(qstring):
    channels = Channel.objects.all()
    return dict((str(channel), Sale.objects.filter(channel=channel).count()) for channel in channels)


def sales_counts(qstring):
    all_skus = api_func('inventory', 'inventoryitem')
    all_sales = UnitSale.objects.all() \
                                .prefetch_related(Prefetch('sku__skuunit__inventory_item'))

    sales_counts = dict((k['label'],0) for k in all_skus)

    for u_sale in all_sales:
        u_sale_counts = u_sale.get_inventory_items()
        for sku in u_sale_counts:
            sales_counts[sku] += u_sale_counts[sku]

    return sales_counts
