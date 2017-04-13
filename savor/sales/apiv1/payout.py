from decimal import Decimal

import sale as sales_api

THRESHOLD = Decimal('2')

def proceeds_rec(qstring):
    paid_thru = qstring.get('paid_thru')

    sales_list = sales_api.sale({'view': 'simple', 'paid_thru': paid_thru})
    gross = dict((s['id'], Decimal(s['total_adjustments'])) 
    				for s in sales_api.sale({'view': 'proceedsadjustments', 'paid_thru': paid_thru}))
    adjusts = dict((s['id'], Decimal(s['gross_proceeds'])) 
    				for s in sales_api.sale({'view': 'grossproceeds', 'paid_thru': paid_thru}))
    salestax = dict((s['id'], Decimal(s['total_salestax'])) 
    				for s in sales_api.sale({'view': 'salestax', 'paid_thru': paid_thru}))
    payouts = dict((s['id'], Decimal(s['total_payout'])) 
    				for s in sales_api.sale({'view': 'payouts', 'paid_thru': paid_thru}))

    for s in sales_list:
    	s['proceeds'] = gross.get(s['id'], Decimal('0')) \
    					+ adjusts.get(s['id'], Decimal('0')) \
    					+ salestax.get(s['id'], Decimal('0'))
    	s['payout'] = payouts.get(s['id'], Decimal('0'))
    	s['unpaid'] = s['proceeds'] - s['payout']
    return [s for s in sales_list if abs(s['unpaid'] > THRESHOLD)]
    