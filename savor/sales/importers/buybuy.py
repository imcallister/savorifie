import os
from decimal import Decimal
import pandas as pd
from dateutil.parser import parse

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect

from ..models import Sale, UnitSale
from parsers import parse_buybuy
import products.models
import accountifie.common.uploaders.csv
from accountifie.toolkit.forms import FileForm
from accountifie.common.api import api_func

DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

"""
def get_product(sku):
    return 'BYE' if sku[:2] == 'BE' else 'SYE'
"""


def get_unitsale(row):
    quantity = int(row['Quantity'])
    unit_price = Decimal(row['Unit Cost'].replace('$', ''))
    sku_code = row['Vendor SKU']
    sku_id = products.models.Product.objects.get(label=sku_code).id

    if quantity != '' and unit_price != '' and sku_id != '':
        return {'quantity': quantity, 'unit_price': unit_price, 'sku_id': sku_id}
    else:
        return None



def order_upload(request):
    form = FileForm(request.POST, request.FILES)

    if form.is_valid():
        upload = request.FILES.values()[0]
        file_name_with_timestamp = accountifie.common.uploaders.csv.save_file(upload)

        rslts = process_buybuy(file_name_with_timestamp)
        if rslts['status'] == 'ERROR':
            messages.warning(request, 'File is not csv. Please check file')
        else:
            dupes = rslts['exist_sales_ctr']
            new_sales = rslts['new_sales_ctr']
            unknown_cp_ctr = rslts['unknown_cp_ctr']
            messages.success(request, 'Loaded shopify file: %d new sales and %d duplicate sales' % (new_sales, dupes))
            messages.warning(request, 'Missing counterparty info: %d not recognised. Please see Shopify report.' % unknown_cp_ctr)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the shopify file provided, please see below')
        return render(request, 'uploaded.html', context)


"""
def parse_buybuy(sales):
    sales = sales[sales['Substatus']!='cancelled']

    sales_items = []
    for k, v in sales.groupby('PO Number'):
        sale_info = {}
        v.fillna('', inplace=True)

        sale_info['company_id'] = 'SAV'
        sale_info['external_channel_id'] = str(v.iloc[0]['PO Number'])
        sale_info['shipping_charge'] = Decimal(str(v.iloc[0]['Shipping']))
        
        sale_info['sale_date'] = parse(v.iloc[0]['Order Date']).date()

        if v.ilov[0]['Sales Division'] == 'buybuy Baby':
            sale_info['channel_id'] = api_func('sales', 'channel', 'BUYBUY')['id']
        else:
            sale_info['channel_id'] = api_func('sales', 'channel', 'BEDBATH')['id']

        company = v.iloc[0]['BillTo Company Name']
        if not np.isnan(company):
            if api_func('gl', 'counterparty', company):
                sale_info['customer_code_id'] = company
            else:
                sale_info['customer_code_id'] = 'unknown'
        else:
            sale_info['customer_code_id'] = 'retail_buyer'

        email = v.iloc[0]['ShipTo Email']
        if not np.isnan(email):
            sale_info['notification_email'] = email
        
        sale_info['shipping_name'] = v.iloc[0]['ShipTo Name']
        sale_info['shipping_company'] = v.iloc[0]['ShipTo Company Name']
        sale_info['shipping_address1'] = v.iloc[0]['ShipTo Address1']
        sale_info['shipping_address2'] = v.iloc[0]['ShipTo Address2']
        sale_info['shipping_city'] = v.iloc[0]['ShipTo City']
        sale_info['shipping_zip'] = v.iloc[0]['ShipTo Postal Code'].replace("'", "")
        sale_info['shipping_province'] = v.iloc[0]['ShipTo State']
        sale_info['shipping_country'] = v.iloc[0]['ShipTo Country']
        sale_info['shipping_phone'] = v.iloc[0]['BillTo Day Phone']

        for idx in v.index:
            obj_data = get_unitsale(v.loc[idx].to_dict())
        
        sale_info['unit_sales'] = obj_data

    sales_items.append(sale_info)
    return sales_items
"""


def process_buybuy(file_name):
    if file_name.split('.')[-1] != 'csv':
        return {'status': 'ERROR', 'msg': 'WRONG_FILE_TYPE'}

    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    sales_items = parse_buybuy(pd.read_csv(incoming_name, skiprows=4).fillna(''))
    
    new_sales_ctr = 0
    exist_sales_ctr = 0
    unknown_cp_ctr = 0

    for s in sales_items:
        sale_obj = Sale.objects.filter(external_channel_id=s['external_channel_id']).first()

        if sale_obj:
            # if sale object already exists ... skip to next one
            exist_sales_ctr += 1
        else:
            new_sales_ctr += 1
            sale_info = dict((k, v) for k, v in s.iteritems() if k != 'unit_sales')
            sale_info['channel_id'] = api_func('sales', 'channel', sale_info['channel_label'])['id']
            del sale_info['channel_label']
            sale_obj = Sale(**sale_info)
            sale_obj.save()

            for us in s['unit_sales']:
                us['sale_id'] = sale_obj.id
                us['sku_id'] = products.models.Product.objects.get(label=us['sku_code']).id
                del us['sku_code']
                us_obj = UnitSale(**us)
                us_obj.save()

    return {'status': 'SUCCESS', 'exist_sales_ctr': exist_sales_ctr,
            'new_sales_ctr': new_sales_ctr, 'unknown_cp_ctr': unknown_cp_ctr}
