from decimal import Decimal
from behave import given

from products.models import Product, ProductLine, InventoryItem, SKUUnit
from inventory.models import Warehouse, Shipment, ShipmentLine
from sales.models import Channel
from accountifie.gl.models import Counterparty

@given(u'there are productlines')
def impl(context):
    for row in context.table:
        ProductLine(description=row['description'],
                    label=row['label']).save()


@given(u'there are channels')
def impl(context):
    for row in context.table:
        Channel(counterparty_id=row['counterparty'], label='SHOPIFY').save()


@given(u'there are inventoryitems')
def impl(context):
    for row in context.table:
        pr_line = ProductLine.objects.filter(label=row['productline']).first()
        InventoryItem(description=row['description'],
                      label=row['label'],
                      master_sku=row['master_sku'],
                      product_line=pr_line).save()


@given(u'there are skuunits')
def impl(context):
    for row in context.table:
        pr = Product.objects.filter(label=row['sku']).first()
        ii = InventoryItem.objects.filter(label=row['inv_item']).first()
        SKUUnit(quantity=row['quantity'],
                inventory_item=ii,
                sku=pr,
                rev_percent=Decimal(row['rev_percent'])).save()

@given(u'there are warehouses')
def impl(context):
    for row in context.table:
        Warehouse(description=row['description'],
                  label=row['label']).save()


@given(u'there are shipments')
def impl(context):
    for row in context.table:
        warehouse = Warehouse.objects.filter(label=row['warehouse']).first()
        sent_by = Counterparty.objects.filter(id=row['sent_by']).first()
        Shipment(arrival_date=row['arrival_date'],
                 description=row['description'],
                 label=row['label'],
                 destination=warehouse,
                 sent_by=sent_by).save()


@given(u'there are shipmentlines')
def impl(context):
    for row in context.table:
        ii = InventoryItem.objects.filter(label=row['inv_item']).first()
        shpmt = Shipment.objects.filter(label=row['shipment']).first()
        ShipmentLine(inventory_item=ii,
                     quantity=row['quantity'],
                     cost=row['cost'],
                     shipment=shpmt).save()


@given(u'a shipmentline is booked')
def impl(context):
    row = context.table[0]
    ii = InventoryItem.objects.filter(label=row['inv_item']).first()
    shpmt = Shipment.objects.filter(label=row['shipment']).first()
    context.bmo = ShipmentLine(inventory_item=ii,
                               quantity=row['quantity'],
                               cost=row['cost'],
                               shipment=shpmt)


@given(u'there are products')
def impl(context):
    for row in context.table:
        Product(description=row['description'],
                label=row['label']).save()


