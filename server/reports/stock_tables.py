import pandas as pd
from decimal import Decimal

import base.models as base
import accountifie.gl.models as gl


def stock_table(start_date, end_date):

    start_entries = base.StockEntry.objects.filter(date__lte=start_date)
    start_df = pd.DataFrame(dict((x.id, x.__dict__) for x in start_entries)).T
    end_entries = base.StockEntry.objects.filter(date__lte=end_date)
    end_df = pd.DataFrame(dict((x.id, x.__dict__) for x in end_entries)).T


    period_entries = base.StockEntry.objects.filter(date__gt=start_date, date__lte=end_date)
    stock_entries = pd.DataFrame(dict((x.id, x.__dict__) for x in period_entries)).T

    
    if not stock_entries.empty:
        table = stock_entries[['gl_acct_id','share_class', 'quantity']].groupby(['gl_acct_id','share_class']).sum()
        table = table.unstack(level=1).fillna(0)['quantity']
        table.index = table.index.map(lambda x: gl.Account.objects.get(id=x).display_name)
    else:
        table = pd.DataFrame(columns=['common', 'series_A1'])
    
    cols = set(end_df['share_class'].values)
    for c in [x for x in cols if x not in table.columns]:
        table[c] = Decimal('0')
    
    table.loc['Shareholder Equity at Start of Period'] = start_df[['share_class','quantity']].groupby('share_class').sum()['quantity']
    table.loc['Shareholder Equity at End of Period'] = end_df[['share_class','quantity']].groupby('share_class').sum()['quantity']
    table.fillna(Decimal('0'),inplace=True)
    table.loc['Change in period'] = table.loc['Shareholder Equity at End of Period'] - table.loc['Shareholder Equity at Start of Period']
    
    return table