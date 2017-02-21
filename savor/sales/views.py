import csv

from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Prefetch
from accountifie.common.api import api_func

from .models import SalesTax, Sale
import importers.shopify
import importers.buybuy


def assign_COGS(request):
    call_command('calc_COGS')
    return HttpResponseRedirect("/maintenance")

@login_required
def shopify_upload(request):
    return importers.shopify.order_upload(request)

@login_required
def buybuy_upload(request):
    return importers.buybuy.order_upload(request)

def __get_salestax_data(obj):
    d = {}
    d['tax']  = obj.tax
    d['order'] = str(obj.sale)
    d['collector'] = obj.collector.entity
    d['sale_date'] = obj.sale.sale_date.isoformat()
    d['gross_proceeds'] = obj.sale.get_gross_proceeds()
    return d


@login_required
def output_salestax(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="salestax.csv"'
    writer = csv.writer(response)

    all_st = SalesTax.objects.all() \
                             .prefetch_related(Prefetch('collector')) \
                             .prefetch_related(Prefetch('sale'))

    header_row = ['order', 'collector', 'sale_date', 'tax', 'gross_proceeds']

    writer.writerow(header_row)
    for st in all_st:
        line = [__get_salestax_data(st).get(c,'') for c in header_row]
        writer.writerow(line)
    return response


@login_required
def allsales_dump(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="allsales.csv"'
    writer = csv.writer(response)

    all_sales = api_func('base', 'sale')

    header_row = ['label', 'channel', 'customer_code', 'shipping_name',
                  'items_string', 'sale_date', 'shipping_company',
                  'notification_email', 'shipping_phone',
                  'shipping_address1', 'shipping_address2', 'shipping_city',
                  'shipping_province', 'shipping_zip', 'shipping_country',
                  ]

    writer.writerow(header_row)
    for sl in all_sales:
        line = [sl.get(f,'') for f in header_row]
        writer.writerow(line)
    return response


def get_primary_tax_collector(st_list):
    if len(st_list) == 0:
        return 'none'
    elif len(st_list) == 1:
        return st_list[0].collector.entity
    elif len(st_list) > 1:
        all_entities = [x.collector.entity for x in st_list]
        return [x for x in all_entities if x!='NY State'][0]


@login_required
def output_grosses(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="salestax.csv"'
    writer = csv.writer(response)

    sales = Sale.objects.all()

    header_row = ['order', 'sale_date', 'proceeds', 'sales_tax', 'primary_collector']
    writer.writerow(header_row)
    for s in sales:
        st_lines = s.salestax_set.all()
        all_tax = sum([st.tax for st in st_lines])
        primary_collector = get_primary_tax_collector(st_lines)
        line = [str(s), s.sale_date.isoformat(), s.get_gross_proceeds(), 
                all_tax, primary_collector]
        writer.writerow(line)
    return response
