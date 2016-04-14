import datetime
from decimal import Decimal
import pandas as pd
from dateutil.parser import parse

from django.conf import settings

from accountifie.reporting.models import Report, BasicBand, TextBand
from accountifie.toolkit.utils import DZERO
from query.query_manager import QueryManager
from accountifie.common.api import api_func
import accountifie.toolkit.utils as utils

import logging

logger = logging.getLogger('default')



class SnapshotRec(Report):
    
    def __init__(self, company_id, date=None):

        self.date = date
        self.snapshot = None
        self.qm_strategy = None
        self.description = 'Account History Reconciliation'
        self.title = None
        self.company_id = company_id
        self.columns = None
        self.column_order = None
        self.calc_type = 'as_of'
        self.set_company()
        self.label_map = None
        self.link_map = None
        self.equity_sign = False

        self.path = None
        self.acct_id = None
        self.works_for = ['SAV']

    
    def calcs(self):
        data = {}
        idx = {}

        snapshot_strategy = QueryManager(gl_strategy=self.qm_strategy) if self.qm_strategy else self.query_manager
        snap_history = snapshot_strategy.pd_history(self.company_id, 'account', self.account_id, from_date=settings.DATE_EARLY, to_date=self.date)
        curr_history = self.query_manager.pd_history(self.company_id, 'account', self.account_id, from_date=settings.DATE_EARLY, to_date=self.date)
        
        self.column_order = ['snapshot', 'current','diff']
        self.columns = dict(zip(self.column_order, self.column_order))

        
        if snap_history.empty:
            snap_bals = pd.Series()
        else:
            snap_bals = snap_history.sort_index(by='date')[['date','amount']].groupby('date').sum()['amount'].cumsum()
        
        if curr_history.empty:
            curr_bals = pd.Series()
        else:
            curr_bals = curr_history.sort_index(by='date')[['date','amount']].groupby('date').sum()['amount'].cumsum()

        bals = pd.DataFrame({'snapshot': snap_bals, 'current': curr_bals}).fillna(method='ffill')
        bals.fillna(0.0, inplace=True)
        for col in ['snapshot', 'current']:
            bals[col] = bals[col].map(lambda x: Decimal(x))
        bals['diff'] = bals['snapshot'] - bals['current']
        
        accts = api_func('gl', 'account')

        acct_map = dict((a['id'], a['display_name']) for a in accts)
        
        label_map = lambda x: x + ': ' + acct_map[x] if x in acct_map else x
        link_map = lambda x: '/snapshot/glsnapshots/rechistory/%s/%s?to=%s'  % (self.snapshot.id, self.account_id, x.name.isoformat())

        bals['fmt_tag'] = 'item'
        bals['label'] = bals.index.map(label_map)
        bals['link'] = bals.apply(link_map, axis=1)

        
        table_data = bals.to_dict(orient='records')

        for row in table_data:
            if row['fmt_tag'] != 'header':
                for col in self.column_order:
                    row[col] = {'text': row[col], 'link': row['link']}
        return table_data


