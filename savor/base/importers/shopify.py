import os
from decimal import Decimal
import pandas as pd
from dateutil.parser import parse

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext

from savor.base.models import Sale, SalesTax, Product, UnitSale, TaxCollector
import accountifie.toolkit
from accountifie.toolkit.forms import FileForm

DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')


def get_product(sku):
    return 'BYE' if sku[:2] == 'BE' else 'SYE'

def get_unitsale(row):
    quantity = int(row['Lineitem quantity'])
    unit_price = row['Lineitem price']
    product_code = get_product(row['Lineitem sku'])
    product_id = Product.objects.get(short_code=product_code).id
    
    if quantity != '' and unit_price != '' and product_id != '':
        return {'quantity': quantity, 'unit_price': unit_price, 'product_id': product_id}
    else:
        return None

def get_taxes(row):
    taxes = []
    for i in range(1,6):
        collector_col = 'Tax %d Name' % i
        amount_col = 'Tax %d Value' % i
        if not row[collector_col]=='':
            taxes.append((row[collector_col].split(' Tax')[0], Decimal(str(row[amount_col]))))
    return taxes       

def order_upload(request):

    
    form = FileForm(request.POST, request.FILES)

    if form.is_valid():
        upload = request.FILES.values()[0]
        file_name = upload._name
        file_name_with_timestamp = accountifie.toolkit.uploader.save_file(upload)
        dupes, new_sales = process_shopify(file_name_with_timestamp)
        messages.success(request, 'Loaded shopify file: %d new sales and %d duplicate sales' %(new_sales, dupes))
        context = {}
        return render_to_response('base/uploaded.html', context, context_instance=RequestContext(request))
    else:
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the shopify file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))


def process_shopify(file_name):
    
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    with open(incoming_name, 'U') as f:
        sales = pd.read_csv(incoming_name)

    new_sales_ctr = 0
    exist_sales_ctr = 0

    sales_items = []
    for k, v in sales.groupby('Name'):
        sale_info = {}
        v.fillna('', inplace=True)
        sale_info['company_id'] = 'SAV'
        sale_info['external_ref'] = str(v.iloc[0]['Name'])
        sale_info['shipping'] = Decimal(str(v.iloc[0]['Shipping']))
        sale_info['discount_code'] = str(v.iloc[0]['Discount Code'])
        if sale_info['discount_code']=='':
            sale_info['discount_code'] = None
            
        sale_info['discount'] = Decimal(v.iloc[0]['Discount Amount'])
        sale_info['sale_date'] = parse(v.iloc[0]['Created at']).date()
        sale_info['channel'] = 'shopify'
        sale_info['customer_code'] = v.iloc[0]['Email']
        sale_info['memo'] = ''
        sale_info['fulfill_status'] = v.iloc[0]['Lineitem fulfillment status']
        if sale_info['fulfill_status'] == 'pending':
            sale_info['fulfill_status'] = 'unfulfilled'
        else:
            sale_info['fulfill_status'] = 'fulfilled'
            
        sales_items.append(sale_info)
        
        sale_obj = Sale.objects.filter(external_ref=sale_info['external_ref']).first()
        
        if sale_obj:
            # if sale object already exists ... skip to next one
            exist_sales_ctr += 1
        else:
            new_sales_ctr += 1
            sale_obj = Sale(**sale_info)
            sale_obj.save()
        
            all_taxes = []
            for idx in v.index:
                all_taxes += get_taxes(v.loc[idx].to_dict())

            # create tax objects    
            for t in all_taxes:
                obj_data = {
                    'collector_id': TaxCollector.objects.get(entity=t[0]).id,
                    'tax': t[1],
                    'sale_id' : sale_obj.id
                    }

                tax_obj = SalesTax(**obj_data)
                tax_obj.save()

            for idx in v.index:
                obj_data = get_unitsale(v.loc[idx].to_dict())
                obj_data['sale_id'] = sale_obj.id

                unitsale_obj = UnitSale(**obj_data)
                unitsale_obj.save()

            sale_obj.save()
    return exist_sales_ctr, new_sales_ctr