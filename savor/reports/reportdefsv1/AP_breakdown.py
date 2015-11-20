import datetime
import pandas as pd
from dateutil.parser import parse

from accountifie.reporting.models import Report, BasicBand, TextBand
from _utils import DZERO
import accountifie.gl.models as gl
import accountifie._utils as utils


class APBreakdown(Report):
    
    def __init__(self, company_id, date=None):

        self.date = date
        self.description = 'AP Breakdown'
        self.title = None
        self.company_id = company_id
        self.columns = None
        self.column_order = None
        self.calc_type = 'as_of'
        self.set_company()
        self.label_map = None
        self.link_map = lambda x: utils.acct_history_link(x.name)

        self.path = None
        self.acct_list = None
        self.works_for = ['SAV']

    def configure(self, as_of=None, col_tag=None, path=None):
        
        cfg = utils.config_fromcoltag(col_tag, self.description, self.calc_type)
        self.title = cfg['title']
        self.dates = (cfg['column_order'][0], cfg['column_order'][2])
        

    def calcs(self):
        data = {}
        idx = {}

        self.columns = {'pos_amount': 'pos_amount', 'neg_amount': 'neg_amount', 'total': 'total'}
        self.column_order = ['pos_amount', 'neg_amount', 'total']


        from_date = parse(self.dates[0]) + datetime.timedelta(days=1)
        bals = self.query_manager.cp_balances(self.company_id, ['3000'],from_date=from_date.isoformat(),to_date=self.dates[1])
        
        
        bals.loc['Total'] = bals.apply(sum, axis=0)
        
        accts = gl.Account.objects.all()
        acct_map = dict((a.id, a.display_name) for a in accts)
        label_map = lambda x: x + ': ' + acct_map[x] if x in acct_map else x
        

        bals['fmt_tag'] = 'item'
        bals['label'] = bals.index.map(label_map)
        bals['link'] = bals.apply(self.link_map, axis=1)

        bals.loc['Total', 'fmt_tag'] = 'major_total'
        data = bals.to_dict(orient='records')

        for row in data:
            for col in self.column_order:
                row[col] = {'text': row[col], 'link': link_map(row)}
        
        return data