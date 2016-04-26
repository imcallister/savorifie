import datetime
from multipledispatch import dispatch

from django.conf import settings
from django.forms.models import model_to_dict

from accountifie.common.api import api_func
from savor.base.models import Sale, UnitSale


def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data

@dispatch(dict)
def sale(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())

    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()

    all_sales = Sale.objects.filter(sale_date__gte=start_date, sale_date__lte=end_date)
    fields=[field.name for field in all_sales[0]._meta.fields]

    return [get_model_data(sale_obj, fields) for sale_obj in all_sales]


@dispatch(unicode, dict)
def sale(id, qstring):
    sale_obj = Sale.objects.get(id=id)
    fields=[field.name for field in sale_obj._meta.fields]
    return get_model_data(sale_obj, fields)


def summary_sales_stats(qstring):
    unit_sales_info = unit_sales(qstring)
    inventory_items = api_func('inventory', 'inventoryitem')
    for item in inventory_items:
        item['sold'] = len([x for x in unit_sales_info if x['inventory item']==item['short_code']])

    stats = dict((item['short_code'], item['sold']) for item in inventory_items)
    return stats


def missing_cps(qstring):
    missing_cp_sales = Sale.objects.filter(customer_code__id='unknown')
    return [model_to_dict(sale, fields=[field.name for field in sale._meta.fields]) for sale in missing_cp_sales]


def sales_counts(qstring):
    all_skus = api_func('inventory', 'inventoryitem')
    all_sales = UnitSale.objects.all()

    sales_counts = dict((k['short_code'],0) for k in all_skus)

    for u_sale in all_sales:
        u_sale_counts = u_sale.get_inventory_items()
        for sku in u_sale_counts:
            sales_counts[sku] += u_sale_counts[sku]

    return sales_counts


@dispatch(unicode, dict)
def sale_skus(sale_id, qstring):
    unit_sales = UnitSale.objects.filter(sale_id=sale_id)

    skus_list = {}
    for u_sale in unit_sales:
        inv_items = u_sale.get_inventory_items()
        for i in inv_items:
            if i in skus_list:
                skus_list[i] += inv_items[i]
            else:
                skus_list[i] = inv_items[i]
    return skus_list


@dispatch(str, dict)
def sale_skus(sale_id, qstring):
    unit_sales = UnitSale.objects.filter(sale_id=sale_id)

    skus_list = {}
    for u_sale in unit_sales:
        inv_items = u_sale.get_inventory_items()
        for i in inv_items:
            if i in skus_list:
                skus_list[i] += inv_items[i]
            else:
                skus_list[i] = inv_items[i]
    return skus_list


@dispatch(unicode, dict)
def unit_sales(sale_id, qstring):
    unit_sales = UnitSale.objects.filter(sale_id=sale_id)
    u_sale_flds = ['sku', 'quantity', 'unit_price']
    return [get_model_data(u_sale, u_sale_flds) for u_sale in unit_sales]


@dispatch(str, dict)
def unit_sales(sale_id, qstring):
    unit_sales = UnitSale.objects.filter(sale_id=sale_id)
    u_sale_flds = ['sku', 'quantity', 'unit_price']
    return [get_model_data(u_sale, u_sale_flds) for u_sale in unit_sales]


@dispatch(dict)
def unit_sales(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())

    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()

    all_unit_sales = UnitSale.objects.filter(sale__sale_date__gte=start_date, sale__sale_date__lte=end_date)

    u_sale_flds = ['sku', 'quantity', 'unit_price']
    sale_flds = ['customer_code', 'memo','sale_date',"channel","external_ref"]

    output_data = []
    for u_sale in all_unit_sales:
        inventory_items = u_sale.get_inventory_items()
        for item in inventory_items:
            data = get_model_data(u_sale, u_sale_flds)
            data['inventory item'] = item
            data['quantity'] = inventory_items[item]
            data.update(get_model_data(u_sale.sale, sale_flds))
            data['sale_link'] = u_sale.sale.id_link
            output_data.append(data)

    return output_data
