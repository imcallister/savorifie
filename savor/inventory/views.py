import csv

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from accountifie.common.api import api_func
from accountifie.common.table import get_table


@login_required
def main(request):
    user = request.user
    context = {}

    inventory_count = api_func('inventory', 'inventorycount')
    context = dict(('%s_count' % k, v) for k,v in inventory_count.iteritems())

    sales_counts = api_func('base', 'sales_counts')
    for sku in sales_counts:
        context['%s_sold' % sku] = int(100.0 * float(sales_counts[sku]) / float(inventory_count[sku]))

    context['unfulfilled'] = get_table('unfulfilled')
    return render_to_response('inventory/main.html', context, context_instance = RequestContext(request))


@login_required
def sales_detail(request):
    context = {}
    context['unit_sales'] = get_table('unit_sales')()

    stats = api_func('base', 'summary_sales_stats')
    context['stats'] = stats.copy()
    return render_to_response('inventory/sales_detail.html', context, context_instance = RequestContext(request))


@login_required
def output_shopify_no_wrap(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shopify_no_wrap.csv"'
    writer = csv.writer(response)

    data = api_func('inventory', 'shopify_no_wrap_request')

    headers = {'id': 'SAVOR ID', 'channel': 'Channel Shipping Name', 'shipping_company': 'Shipping Company',
                'shipping_address1': 'Shipping Address1', 'shipping_address2': 'Shipping Address2',
                'shipping_city': 'Shipping City', 'shipping_zip': 'Shipping Zip', 'shipping_province': 'Shipping Province',
                'shipping_country': 'Shipping Country', 'shipping_phone': 'Shipping Phone',
                'notification_email': 'Email', 'shipping_company': 'Shipping Company', 'shipping_type': 'Shipping Type',
                'bill_to': 'Bill To', 'gift_message': 'Gift Message', 'skus:sku': 'Lineitem sku',
                'skus:name': 'Lineitem name', 'skus:quantity': 'Lineitem quantity'}
    
    header_row = [unicode(headers[x]).encode('utf-8') for x in headers]

    writer.writerow(header_row)
    """
    for ex in all_expenses:
        line = [unicode(x).encode('utf-8') for x in ex.__dict__.values()]
        writer.writerow(line)
    """
    return response


@login_required
def fulfill_request(request):
    
    # 1 get unfulfilled & split into bucket
    unfulfilled = api_func('inventory', 'unfulfilled')

    shopify_no_wrap = [odr for odr in unfulfilled if odr['gift_wrapping']=='False' and odr['channel']=='Shopify']
    shopify_wrap = [odr for odr in unfulfilled if odr['gift_wrapping']!='False' and odr['channel']=='Shopify']

    # still need transfers and Grommet

    # 3 get shipping info
    # shopify no wrap shipping

    shopify_standard = api_func('inventory', 'channelshipmenttype', 'SHOP_STANDARD')
    for odr in shopify_no_wrap:
        odr['ship_type'] = shopify_standard['ship_type']
        odr['bill_to'] = shopify_standard['bill_to']


    context = {}
    context['unit_sales'] = get_table('unit_sales')()

    stats = api_func('base', 'summary_sales_stats')
    context['stats'] = stats.copy()
    return render_to_response('inventory/sales_detail.html', context, context_instance = RequestContext(request))
