from decimal import Decimal

SHOPIFY_PCT_FEE = Decimal('0.026')
SHOPIFY_PER_FEE = Decimal('0.3')

FBA_PCT_FEE = Decimal('0.15')
FBA_PER_FEE = Decimal('6.35')

def shopify_fee(sale_obj, adjust_amounts):
    total = sale_obj.gross_sale_proceeds() + adjust_amounts
    total += sale_obj.total_sales_tax()
    return total * SHOPIFY_PCT_FEE + SHOPIFY_PER_FEE


def FBA_fee(sale_obj):
	qty = sum(u['quantity'] for u in sale_obj.unit_sale.all().values('quantity'))
	return qty * FBA_PER_FEE + FBA_PCT_FEE * sale_obj.gross_sale_proceeds()