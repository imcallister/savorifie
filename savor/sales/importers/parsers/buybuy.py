from decimal import Decimal
from dateutil.parser import parse


def get_unitsale(row):
    quantity = int(row['Quantity'])
    unit_price = Decimal(row['Unit Cost'].replace('$', ''))
    sku_code = row['Vendor SKU'].strip()
    
    if quantity != '' and unit_price != '' and sku_code != '':
        return {'quantity': quantity, 'unit_price': unit_price, 'sku_code': sku_code}
    else:
        return None

def parse_buybuy(sales):
    sales = sales[sales['Substatus']!='cancelled']

    sales_items = []
    
    for k, v in sales.groupby('PO Number'):
        sale_info = {}
        
        sale_info['company_id'] = 'SAV'
        sale_info['external_channel_id'] = str(v.iloc[0]['PO Number'])
        sale_info['shipping_charge'] = Decimal(str(v.iloc[0]['Shipping']).replace('$', ''))
        
        sale_info['sale_date'] = parse(v.iloc[0]['Order Date']).date()

        if v.iloc[0]['Sales Division'] == 'buybuy Baby':
            sale_info['channel_label'] = 'BUYBUY'
        else:
            sale_info['channel_label'] = 'BEDBATH'

        company = v.iloc[0]['BillTo Company Name']
        if company != '':
            sale_info['customer_code_id'] = 'unknown'
        else:
            sale_info['customer_code_id'] = 'retail_buyer'

        email = v.iloc[0]['ShipTo Email']
        if email != '':
            sale_info['notification_email'] = email
        
        sale_info['shipping_name'] = v.iloc[0]['ShipTo Name']
        sale_info['shipping_company'] = v.iloc[0]['ShipTo Company Name']
        sale_info['shipping_address1'] = v.iloc[0]['ShipTo Address1']
        sale_info['shipping_address2'] = v.iloc[0]['ShipTo Address2']
        sale_info['shipping_city'] = v.iloc[0]['ShipTo City']
        sale_info['shipping_zip'] = v.iloc[0]['ShipTo Postal Code'].replace("'", "")
        sale_info['shipping_province'] = v.iloc[0]['ShipTo State']
        sale_info['shipping_country'] = v.iloc[0]['ShipTo Country']
        sale_info['shipping_phone'] = v.iloc[0]['BillTo Day Phone']

        sale_info['unit_sales'] = []
        for idx in v.index:
            sale_info['unit_sales'].append(get_unitsale(v.loc[idx].to_dict()))
        
        sales_items.append(sale_info)

    return sales_items