from multipledispatch import dispatch

from django.forms.models import model_to_dict

from inventory.models import SKU, InventoryItem, ProductLine


@dispatch(dict)
def sku(qstring):
    all_skus = SKU.objects.all()
    data = []
    for sku in all_skus:
        d = model_to_dict(sku)
        sku_items = list(sku.skuunit_set.all().values())

        for item in sku_items:
            inv_item = model_to_dict(InventoryItem.objects.get(id=item['inventory_item_id']))
            item.update(inv_item)

        d['sku_items'] = sku_items
        data.append(d)
    return data


@dispatch(str, dict)
def sku(short_code, qstring):
    sku = SKU.objects.get(short_code=short_code)

    d = model_to_dict(sku)
    sku_items = list(sku.skuunit_set.all().values())

    for item in sku_items:
        inv_item = model_to_dict(InventoryItem.objects.get(id=item['inventory_item_id']))
        item.update(inv_item)
    d['sku_items'] = sku_items

    return d

@dispatch(dict)
def inventoryitem(qstring):
    items = InventoryItem.objects.all()
    all_data = []

    for item in items:
        product_line = item.product_line
        item_data = model_to_dict(item)
        product_line_data = dict(('Product Line %s' %k, v) for k,v in model_to_dict(product_line).iteritems())
        
        data = item_data
        data.update(product_line_data)
        all_data.append(data)

    return all_data
    

@dispatch(str, dict)
def inventoryitem(short_code, qstring):
    item = InventoryItem.objects.get(short_code=short_code)
    product_line = item.product_line

    item_data = model_to_dict(item)
    product_line_data = dict(('Product Line %s' %k, v) for k,v in model_to_dict(product_line).iteritems())
    
    data = item_data
    data.update(product_line_data)
    return data

