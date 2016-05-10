import os
from decimal import Decimal
import pandas as pd
from dateutil.parser import parse

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from savor.base.models import Sale, SalesTax, UnitSale, TaxCollector
import inventory.models
import accountifie.toolkit
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
    quantity = int(row['Lineitem quantity'])
    unit_price = row['Lineitem price']
    sku_code = row['Lineitem sku']
    sku_id = inventory.models.Product.objects.get(label=sku_code).id

    if quantity != '' and unit_price != '' and sku_id != '':
        return {'quantity': quantity, 'unit_price': unit_price, 'sku_id': sku_id}
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
        dupes, new_sales, unknown_cp_ctr = process_shopify(file_name_with_timestamp)
        messages.success(request, 'Loaded shopify file: %d new sales and %d duplicate sales' % (new_sales, dupes))
        messages.warning(request, 'Missing counterparty info: %d not recognised. Please see Shopify report.' % unknown_cp_ctr)
        context = {}
        #return render_to_response('base/uploaded.html', context, context_instance=RequestContext(request))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the shopify file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))


def process_shopify(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    with open(incoming_name, 'U') as f:
        sales = pd.read_csv(incoming_name)

    # any pre-formatting of data here
    sales['Shipping Zip'] = sales['Shipping Zip'].map(lambda x: str(x).replace("'",""))

    new_sales_ctr = 0
    exist_sales_ctr = 0
    unknown_cp_ctr = 0

    sales_items = []
    for k, v in sales.groupby('Name'):
        sale_info = {}
        v.fillna('', inplace=True)

        # set default values
        sale_info['gift_wrapping'] = False
        sale_info['gift_wrap_fee'] = Decimal('0')
        sale_info['gift_message'] = None
        for idx in v.index:
            if v.loc[idx, 'Note Attributes'] != '':
                sale_info['gift_message'] = v.loc[idx, 'Note Attributes']

        # check for giftwrap option
        for idx in v.index:
            if v.loc[idx, 'Lineitem name'] == 'Gift Wrap - Custom':
                sale_info['gift_wrapping'] = True
                sale_info['gift_wrap_fee'] = v.loc[idx, 'Lineitem price']

        sale_info['company_id'] = 'SAV'
        sale_info['external_channel_id'] = str(v.iloc[0]['Name'])
        sale_info['shipping_charge'] = Decimal(str(v.iloc[0]['Shipping']))

        shipping_code_string = v.iloc[0]['Shipping Method']
        sale_info['shipping_code'] = 'standard' if shipping_code_string.lower() == 'standard shipping' else 'custom'
        sale_info['discount_code'] = str(v.iloc[0]['Discount Code'])
        if sale_info['discount_code']=='':
            sale_info['discount_code'] = None

        sale_info['discount'] = Decimal(v.iloc[0]['Discount Amount'])
        sale_info['sale_date'] = parse(v.iloc[0]['Created at']).date()
        sale_info['channel_id'] = api_func('base', 'channel', 'SHOPIFY')['id']

        company = v.iloc[0]['Billing Company']
        if company != '':
            if api_func('gl', 'counterparty', company):
                # it exists
                sale_info['customer_code_id']  = company
            else:
                unknown_cp_ctr += 1
                sale_info['customer_code_id']  = 'unknown'
        else:
            sale_info['customer_code_id'] = 'retail_buyer'

        sale_info['notification_email'] = v.iloc[0]['Email']
        sale_info['memo'] = v.iloc[0]['Notes']

        sale_info['shipping_name'] = v.iloc[0]['Shipping Name']
        sale_info['shipping_company'] = v.iloc[0]['Shipping Company']
        sale_info['shipping_address1'] = v.iloc[0]['Shipping Address1']
        sale_info['shipping_address2'] = v.iloc[0]['Shipping Address2']
        sale_info['shipping_city'] = v.iloc[0]['Shipping City']
        sale_info['shipping_zip'] = v.iloc[0]['Shipping Zip'].replace("'", "")
        sale_info['shipping_province'] = v.iloc[0]['Shipping Province']
        sale_info['shipping_country'] = v.iloc[0]['Shipping Country']
        sale_info['shipping_phone'] = v.iloc[0]['Shipping Phone']

        sales_items.append(sale_info)
        sale_obj = Sale.objects.filter(external_channel_id=sale_info['external_channel_id']).first()

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
                tax_collector, created = TaxCollector.objects.get_or_create(entity=t[0])
                obj_data = {
                    'collector_id': tax_collector.id,
                    'tax': t[1],
                    'sale_id' : sale_obj.id
                }

                tax_obj = SalesTax(**obj_data)
                tax_obj.save()

            for idx in v.index:
                # check whether it is gift wrapping or not
                if v.loc[idx, 'Lineitem sku'] != 'GW001':
                    obj_data = get_unitsale(v.loc[idx].to_dict())
                    obj_data['sale_id'] = sale_obj.id

                    unitsale_obj = UnitSale(**obj_data)
                    unitsale_obj.save()

            sale_obj.save()
    return exist_sales_ctr, new_sales_ctr, unknown_cp_ctr
