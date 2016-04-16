import datetime

from django.conf import settings
from django.forms.models import model_to_dict

from accountifie.common.api import api_func
from savor.base.models import Sale, UnitSale

def get_model_data(instance, flds):
    data = dict((fld, str(getattr(instance, fld))) for fld in flds)
    return data

def sales(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())

    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()

    all_sales = Sale.objects.filter(sale_date__gte=start_date, sale_date__lte=end_date)

    return [model_to_dict(sale, fields=[field.name for field in sale._meta.fields]) for sale in all_sales]


def summary_sales_stats(qstring):
    
    unit_sales_info = unit_sales(qstring)
    
    inventory_items = api_func('inventory', 'inventoryitem')
    for item in inventory_items:
        item['sold'] = len([x for x in unit_sales_info if x['inventory item']==item['short_code']])
    
    stats = dict((item['short_code'], item['sold']) for item in inventory_items)
    return stats


def unit_sales(qstring):
    start_date = qstring.get('from_date', settings.DATE_EARLY)
    end_date = qstring.get('to_date', datetime.datetime.now().date())

    if type(start_date) != datetime.date:
        start_date = parse(start_date).date()
    if type(end_date) != datetime.date:
        end_date = parse(end_date).date()

    all_unit_sales = UnitSale.objects.filter(sale__sale_date__gte=start_date, sale__sale_date__lte=end_date)
    
    
    u_sale_flds = ['sku', 'quantity', 'unit_price']
    sale_flds = ['customer_code', 'memo',"fulfill_status",'sale_date',"channel","external_ref"]

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
