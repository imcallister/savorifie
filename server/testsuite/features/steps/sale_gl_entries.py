from behave import given
from decimal import Decimal

from sales.models import Sale, UnitSale, Channel, ProceedsAdjustment
from products.models import Product
from accounting.models import COGSAssignment

import logging
logger = logging.getLogger('default')

@given(u'a new sale')
def impl(context):
    row = context.table[0]
    channel = Channel.objects.filter(counterparty_id=row['channel']).first()
    sale = Sale(id=row['id'],
                company_id=row['company'],
                sale_date=row['sale_date'],
                channel=channel,
                special_sale=row.get('special_sale', None),
                customer_code_id=row['customer_code'],
                )
    sale.save(update_gl=False)
    context.bmo = sale


@given(u'new unitsales')
def impl(context):
    for row in context.table:
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

@given(u'new adjustments')
def impl(context):
    for row in context.table:
        ProceedsAdjustment(id=row['id'],
                           sale_id=row['sale'],
                           amount=row['amount'],
                           date=row['date'],
                           adjust_type=row['adjust_type']
                           ).save()
