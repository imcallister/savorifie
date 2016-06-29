from behave import *

from inventory.models import *
from base.models import *

@given(u'there are productlines')
def impl(context):
    for row in context.table:
        ProductLine(description=row['description'],
                    label=row['label']).save()


@given(u'there are channels')
def impl(context):
    for row in context.table:
        Channel(counterparty_id=row['counterparty']).save()



@given(u'there are inventoryitems')
def impl(context):
    for row in context.table:
        InventoryItem(description=row['description'],
                      label=row['label'],
                      master_sku=row['master_sku'],
                      product_line_id=row['productline']).save()


@given(u'there are skuunits')
def impl(context):
    for row in context.table:
        pr = Product.objects.filter(label=row['sku']).first()
        ii = InventoryItem.objects.filter(label=row['inv_item']).first()
        SKUUnit(quantity=row['quantity'],
                inventory_item=ii,
                sku=pr).save()


@given(u'there are warehouses')
def impl(context):
    for row in context.table:
        Warehouse(description=row['description'],
                  label=row['label']).save()


@given(u'there are shipments')
def impl(context):
    for row in context.table:
        Shipment(arrival_date=row['arrival_date'],
                 description=row['description'],
                 label=row['label'],
                 destination_id=row['warehouse']).save()


@given(u'there are shipmentlines')
def impl(context):
    for row in context.table:
        ii = InventoryItem.objects.filter(label=row['inv_item']).first()
        shpmt = Shipment.objects.filter(label=row['shipment']).first()
        ShipmentLine(inventory_item=ii,
                     quantity=row['quantity'],
                     cost=row['cost'],
                     shipment=shpmt).save()


@given(u'there are products')
def impl(context):
    for row in context.table:
        Product(description=row['description'],
                label=row['label']).save()


