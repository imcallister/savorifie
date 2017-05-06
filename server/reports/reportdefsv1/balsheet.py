import datetime
import pandas as pd
from dateutil.parser import parse

from accountifie.reporting.models import Report, BasicBand, TextBand
import accountifie.gl.models
from accountifie.toolkit.utils import DZERO
import accountifie.toolkit.utils as utils


class BalanceSheet(Report):
    
    def __init__(self, company_id, date=None):
        config = {'description': 'Balance Sheet',
                  'calc_type': 'as_of',
                  'date': date}
        
        super(BalanceSheet, self).__init__(company_id, **config)

        self.label_map = utils.get_alias
        self.link_map = utils.path_history_link
        self.works_for = ['SAV']

    
    def calcs(self):
        table_data = []
        
        for table_path in ['assets', 'liabilities', 'equity']:

            header = {'fmt_tag': 'header', 'label': self.label_map(table_path)}
            table_data.append(header)

            table_paths = utils.order_paths(accountifie.gl.models.get_child_paths(table_path))
            
            path_totals = pd.Series(index=self.column_order)
            path_totals = 0

            for path in table_paths:
                if table_path == 'equity':
                    bals = self.query_manager.pd_path_balances(self.company_id, self.columns, [path])
                else:
                    bals = self.query_manager.path_drilldown(self.company_id, self.columns, path)

                if bals is not None:
                    if table_path == 'assets':
                        for col in bals.columns:
                            bals = bals * (-1.0)
                    bals['fmt_tag'] = 'item'
                    bals['label'] = bals.index.map(self.label_map)
                    bals['link'] = bals.index.map(self.link_map)

                    totals = bals[self.column_order].sum(axis=0)
                    path_totals = path_totals + totals

                    totals['fmt_tag'] = 'minor_total'
                    totals['label'] = 'Total %s' % self.label_map(path)
                    totals['link'] = ''
                    bals.loc['Total %s' % self.label_map(path)] = totals

                    bals['index'] = bals.index
                    table_data += bals.to_dict(orient='records')

            path_totals['fmt_tag'] = 'major_total'
            path_totals['label'] = 'Total %s' % self.label_map(table_path)
            path_totals['link'] = ''
            path_totals['index'] = table_path
            table_data.append(path_totals.to_dict())
        
        
        for row in table_data:
            if row['fmt_tag'] != 'header':
                for col in self.column_order:
                    row[col] = {'text': row[col], 'link': row['link']}
        
    
        return table_data