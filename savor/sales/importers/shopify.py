import os
from decimal import Decimal
import pandas as pd
from dateutil.parser import parse

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect

from ..models import Sale, SalesTax, UnitSale, TaxCollector, ProceedsAdjustment
import products.models
import accountifie.common.uploaders.csv
from accountifie.toolkit.forms import FileForm
from accountifie.common.api import api_func

DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')


SHOPIFY_PCT_FEE = Decimal('0.029')
SHOPIFY_PER_FEE = Decimal('0.3')


def get_unitsale(row):
    quantity = int(row['Lineitem quantity'])
    unit_price = row['Lineitem price']
    sku_code = row['Lineitem sku']
    sku_id = products.models.Product.objects.get(label=sku_code).id

    if quantity != '' and unit_price != '' and sku_id != '':
        return {'quantity': quantity, 'unit_price': unit_price, 'sku_id': sku_id}
    else:
        return None


def get_taxes(row):
    taxes = []
    for i in range(1, 6):
        collector_col = 'Tax %d Name' % i
        amount_col = 'Tax %d Value' % i
        if not row[collector_col] == '':
            taxes.append((row[collector_col].split(' Tax')[0], Decimal(str(row[amount_col]))))
    return taxes


def order_upload(request):
    form = FileForm(request.POST, request.FILES)

    if form.is_valid():
        upload = request.FILES.values()[0]
        file_name = upload._name
        file_name_with_timestamp = accountifie.common.uploaders.csv.save_file(upload)

        rslts = process_shopify(file_name_with_timestamp)
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
        context = {'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None}
        messages.error(request, 'Could not process the shopify file provided, please see below')
        return render(request, 'uploaded.html', context)


def shopify_fee(sale_obj):
    sale_obj._get_unit_sales()
    sale_obj._get_sales_taxes()
    total = sale_obj.gross_sale_proceeds()
    if sale_obj.discount:
        total -= Decimal(sale_obj.discount)
    if sale_obj.shipping_charge:
        total += Decimal(sale_obj.shipping_charge)
    if sale_obj.gift_wrap_fee:
        total += Decimal(sale_obj.gift_wrap_fee)
    total += sale_obj.total_sales_tax()
    return total * SHOPIFY_PCT_FEE + SHOPIFY_PER_FEE

PAID_THRU = {
    'Shopify Payments': 'SHOPIFY',
    'PayPal Express Checkout': 'PAYPAL',
    'Amazon Payments': 'AMZN_PMTS'
}


def customer_code(billing_company):
    if billing_company != '':
        if api_func('gl', 'counterparty', billing_company):
            # it exists
            return billing_company
        else:
            return 'unknown'
    else:
        return 'retail_buyer'

def discount_code(disc_code):
    if disc_code == '':
        return None
    else:
        return disc_code



def process_shopify(file_name):
    if file_name.split('.')[-1] != 'csv':
        return {'status': 'ERROR', 'msg': 'WRONG_FILE_TYPE'}

    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    with open(incoming_name, 'U') as f:
        sales = pd.read_csv(incoming_name)

    # any pre-formatting of data here
    sales['Shipping Zip'] = sales['Shipping Zip'].map(lambda x: str(x).replace("'", ""))

    new_sales_ctr = 0
    exist_sales_ctr = 0
    unknown_cp_ctr = 0

    for k, v in sales.groupby('Name'):
        sale_info = {}
        v.fillna('', inplace=True)

        sale_info['company_id'] = 'SAV'
        sale_info['external_channel_id'] = str(v.iloc[0]['Name'])
        sale_info['paid_thru_id'] = PAID_THRU.get(v.iloc[0]['Payment Method'])
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
        sale_info['sale_date'] = parse(v.iloc[0]['Created at']).date()
        sale_info['channel_id'] = api_func('sales', 'channel', 'SHOPIFY')['id']
        sale_info['discount_code'] = discount_code(str(v.iloc[0]['Discount Code']))
        sale_info['customer_code_id'] = customer_code(v.iloc[0]['Billing Company'])
        
        for idx in v.index:
            if v.loc[idx, 'Note Attributes'] != '':
                sale_info['gift_message'] = v.loc[idx, 'Note Attributes']

            if v.loc[idx, 'Lineitem sku'].lower() == 'gw001':
                sale_info['gift_wrapping'] = True
                gift_wrap_fee = v.loc[idx, 'Lineitem price']

        
        if Sale.objects.filter(external_channel_id=sale_info['external_channel_id']).first():
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
                    'sale_id': sale_obj.id
                }

                tax_obj = SalesTax(**obj_data)
                tax_obj.date = sale_obj.sale_date
                tax_obj.save()

            for idx in v.index:
                # check whether it is gift wrapping or not
                if v.loc[idx, 'Lineitem sku'] != 'GW001':
                    obj_data = get_unitsale(v.loc[idx].to_dict())
                    obj_data['sale_id'] = sale_obj.id

                    unitsale_obj = UnitSale(**obj_data)
                    unitsale_obj.date = sale_obj.sale_date
                    unitsale_obj.save()

            pa = {}
            pa['amount'] = shopify_fee(sale_obj)
            if pa['amount'] != Decimal('0'):
                pa['date'] = sale_obj.sale_date
                pa['sale_id'] = sale_obj.id
                pa['adjust_type'] = 'CHANNEL_FEES'
                ProceedsAdjustment(**pa).save()

            pa = {}
            pa['amount'] = Decimal(v.iloc[0]['Discount Amount'])
            if pa['amount'] != Decimal('0'):
                pa['date'] = sale_obj.sale_date
                pa['sale_id'] = sale_obj.id
                pa['adjust_type'] = 'DISCOUNT'
                ProceedsAdjustment(**pa).save()

            pa = {}
            pa['amount'] = Decimal(str(v.iloc[0]['Shipping']))
            if pa['amount'] != Decimal('0'):
                pa['date'] = sale_obj.sale_date
                pa['sale_id'] = sale_obj.id
                pa['adjust_type'] = 'SHIPPING_CHARGE'
                ProceedsAdjustment(**pa).save()

            if sale_obj.gift_wrapping:
                pa = {}
                pa['amount'] = gift_wrap_fee
                pa['date'] = sale_obj.sale_date
                pa['sale_id'] = sale_obj.id
                pa['adjust_type'] = 'GIFTWRAP_FEES'
                ProceedsAdjustment(**pa).save()

            if sale_info['customer_code_id'] == 'unknown':
                unknown_cp_ctr += 1
        
            sale_obj.save()
            
    return {'status': 'SUCCESS', 'exist_sales_ctr': exist_sales_ctr,
            'new_sales_ctr': new_sales_ctr, 'unknown_cp_ctr': unknown_cp_ctr}
