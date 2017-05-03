from sales.models import Sale


def order_loads(qstring):
    output = []
    FBA = max([s['sale_date'] for s in Sale.objects.filter(channel__label='AMZN').values('sale_date')])
    output.append({'Upload': 'Amazon', 'Last Upload': FBA})
    
    shopify = max([s['sale_date'] for s in Sale.objects.filter(channel__label='SHOPIFY').values('sale_date')])
    output.append({'Upload': 'Shopify', 'Last Upload': shopify})
    return output
    