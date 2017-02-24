from dateutil.parser import parse
import datetime
from dateutil.rrule import rrule, MONTHLY
import itertools

import sales.apiv1 as sales_api



def sales_by_month(qstring):

    def keyfunc(x):
        d  = x['date']
        return datetime.date(d.year, d.month, 1)

    all_us_list = [[{'date': i['sale_date'], 'item': k, 'qty': v} for k,v in i['items'].iteritems()] for i in sales_api.unitsaleitems({})]
    all_us = sorted(list(itertools.chain.from_iterable(all_us_list)), key=keyfunc)
    items_list = list(set([u['item'] for u in all_us]))

    monthly = {}
    for item in items_list:
        item_l = [l for l in all_us if l['item'] == item]
        by_month = itertools.groupby(item_l, key=keyfunc)
        monthly[item] = dict((k, sum(j['qty'] for j in g)) for k, g in by_month)
        
    first_date = min(min(d for d in monthly[item]) for item in monthly)
    last_date = max(max(d for d in monthly[item]) for item in monthly)
    
    output = {}
    dates_list = [dt.date() for dt in rrule(MONTHLY, dtstart=first_date, until=last_date)]
    
    output = []
    for d in dates_list:
        rslts = dict((item, monthly.get(item, {}).get(d, 0)) for item in items_list)
        rslts['date'] = d.isoformat()
        output.append(rslts)

    return output
    
    
