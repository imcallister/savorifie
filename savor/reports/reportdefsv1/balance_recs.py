import datetime
import pandas as pd
from dateutil.parser import parse


from financifie.reporting.models import Report, BasicBand, TextBand
from _utils import DZERO
from query.query_manager import QueryManager
import financifie.gl.api
import financifie._utils as utils


class RecBalances(Report):
    
    def __init__(self, company_id, date=None):

        self.date = date
        self.snapshot = None
        self.qm_strategy = None
        self.description = 'Account Balance Reconciliation'
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
        self.acct_list = None
        self.works_for = ['SAV']

    
    def calcs(self):
        data = {}
        idx = {}

        self.link_map = lambda x: '/snapshot/glsnapshots/reconcile/%s/%s?date=%s'  % (self.snapshot.id, x, self.snapshot.closing_date.isoformat())

        snapshot_strategy = QueryManager(gl_strategy=self.qm_strategy) if self.qm_strategy else self.query_manager
        snap_bals = snapshot_strategy.pd_acct_balances(self.company_id,{'snapshot': self.date}).fillna(DZERO)
        curr_bals = self.query_manager.pd_acct_balances(self.company_id,{'current': self.date}).fillna(DZERO)

        self.column_order = ['snapshot', 'current','diff']

        bals = pd.concat([snap_bals, curr_bals], axis=1).fillna(0.0)
        bals['diff'] = bals['current'] - bals['snapshot']
        bals.loc['Total'] = bals.apply(sum, axis=0)
        
        accts = financifie.gl.api.accounts({})

        acct_map = dict((a['id'], a['display_name']) for a in accts)
        label_map = lambda x: x + ': ' + acct_map[x] if x in acct_map else x
        

        bals['fmt_tag'] = 'item'
        bals['label'] = bals.index.map(label_map)
        bals['link'] = bals.index.map(self.link_map)

        bals.loc['Total', 'fmt_tag'] = 'major_total'

        table_data = bals.to_dict(orient='records')

        for row in table_data:
            if row['fmt_tag'] != 'header':
                for col in self.column_order:
                    row[col] = {'text': row[col], 'link': row['link']}
        return table_data
