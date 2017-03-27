from behave import *
from decimal import Decimal

from sales.models import Sale, UnitSale, Channel
from products.models import Product
from accounting.models import COGSAssignment

import logging
logger = logging.getLogger('default')

@given(u'a new sale')
def impl(context):
    row = context.table[0]
    channel = Channel.objects.filter(counterparty_id=row['channel']).first()
    context.bmo = Sale(id=row['id'],
                       company_id=row['company'],
                       sale_date=row['sale_date'],
                       channel=channel,
                       special_sale=row.get('special_sale', None),
                       customer_code_id=row['customer_code'],
                       shipping_charge=Decimal(row['shipping_charge']),
                       discount=Decimal(row.get('discount', 0)))


@given(u'new unitsales')
def impl(context):
    row = context.table[0]
    pr = Product.objects.filter(label=row['sku']).first()
    UnitSale(id=row['id'],
             sale_id=row['sale'],
             sku=pr,
             quantity=int(row['quantity']),
             unit_price=Decimal(row['unit_price']),
             date=row['date']).save()



@given(u'a COGSassignment')
def impl(context):
    row = context.table[0]
    COGSAssignment(shipment_line_id=row['shipment_line'],
                   unit_sale_id=row['unitsale'],
                   quantity=int(row['quantity'])).save()
