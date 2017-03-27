from behave import *
from hamcrest import *
from decimal import Decimal
import flatdict

from accountifie.common.api import api_func
from sales.models import Sale, UnitSale, Channel
from products.models import Product

@given(u'a sale exists')
def impl(context):
    row = context.table[0]
    channel = Channel.objects.filter(counterparty_id=row['channel']).first()
    Sale(company_id=row['company'],
         sale_date=row['sale_date'],
         external_channel_id=row['external_channel_id'],
         channel=channel,
         special_sale=row.get('special_sale', None),
         customer_code_id=row['customer_code'],
         shipping_charge=Decimal(row['shipping_charge']),
         discount=Decimal(row.get('discount', 0))).save(update_gl=False)


@given(u'unitsales exist')
def impl(context):
    row = context.table[0]
    pr = Product.objects.filter(label=row['sku']).first()
    sale = Sale.objects.get(external_channel_id=row['sale'])
    UnitSale(sale_id=sale.id,
             sku=pr,
             quantity=int(row['quantity']),
             unit_price=Decimal(row['unit_price']),
             date=sale.sale_date).save()




@when(u'we call the sales.sale api')
def impl(context):
    context.api_results = [dict(d) for d in api_func('sales', 'sale')]


@then(u'the api results should be')
def impl(context):
    rslts = [flatdict.FlatDict(d) for d in context.api_results]
    expected = [(row['label'],
                 row['customer_code'],
                 row['external_channel_id'],
                 row['sale_date']
                 )
                for row in context.table]
    assert_that(dict(context.api_results), equal_to((expected)))