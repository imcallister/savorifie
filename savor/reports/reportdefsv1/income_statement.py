import datetime
from decimal import Decimal
import pandas as pd
from dateutil.parser import parse

from financifie.reporting.models import Report, BasicBand, TextBand
from _utils import DZERO
import _utils as utils


class IncomeStatement(Report):
    
    def __init__(self, company_id, date=None):

        self.date = date
        self.description = 'Income Statement'
        self.title = None
        self.company_id = company_id
        self.columns = None
        self.column_order = None
        self.calc_type = 'diff'
        self.set_company()
        self.label_map = utils.get_alias
        self.link_map = utils.path_history_link

        self.works_for = ['SAV']

    
    def get_total(self, tbl, fmt_tag, path):
        totals = tbl[self.columns.keys()].apply(lambda x: Decimal(sum(x)), axis=0)
        totals = totals.append(pd.Series({'fmt_tag': fmt_tag, 'link': self.link_map(path), 'label': 'Total %s' % self.label_map(path)}))
        return totals

    def calcs(self):
        table_data = []

        top_level_paths = ['equity.retearnings.' + x for x in ['income', 'opexp']]

        path_totals = {}
        for table_path in top_level_paths:
            header = {'fmt_tag': 'header', 'label': self.label_map(table_path).upper()}
            table_data.append(header)


            table_list = []
            income = self.query_manager.path_drilldown(self.company_id, self.columns, table_path, excl_contra=['4150'])
            
            if len(income) > 0:
                income['fmt_tag'] = 'item'
                income['label'] = income.index.map(self.label_map)
                income['link'] = income.index.map(self.link_map)

                totals = income[self.column_order].sum(axis=0)
                path_totals[table_path] = totals.copy()
                totals['fmt_tag'] = 'minor_total'
                totals['label'] = 'Total %s' % self.label_map(table_path)
                totals['link'] = ''
                income.loc['Total %s' % self.label_map(table_path)] = totals
            else: # no data, add only a total row of zeros
                income = pd.DataFrame(index=[table_path], columns=self.column_order).fillna(DZERO)
                income['fmt_tag'] = 'minor_total'
                income['label'] = income.index.map(self.label_map)
                income['link'] = income.index.map(self.link_map)

            table_data += income.to_dict(orient='records')
            
        other_expense_data = []
        for path in ['equity.retearnings.' + x for x in ['interestexpense', 'taxexp', 'gainloss']]:
            other_expense_data.append(self.query_manager.pd_path_balances(self.company_id, self.columns, [path], excl_contra=['4150'])) 
        other_expenses = pd.concat(other_expense_data)

        path_totals['other_expenses'] = other_expenses.sum(axis=0)

        other_expenses['label'] = other_expenses.index.map(self.label_map)
        other_expenses['fmt_tag'] = 'item'
        other_expenses['link'] = other_expenses.index.map(self.link_map)
        
        table_data += other_expenses.to_dict(orient='records')

        net_income = pd.DataFrame(path_totals).sum(axis=1)
        net_income['label'] = 'Net Income'
        net_income['fmt_tag'] = 'major_total'
        net_income['link'] = ''
        table_data += [net_income.to_dict()]

        for row in table_data:
            if row['fmt_tag'] != 'header':
                for col in self.column_order:
                    row[col] = {'text': row[col], 'link': row['link']}
        
        
        return table_data

    def extra_info(self, df, fmt_tag):
        df['label'] = df.index.map(self.label_map)
        df['link'] = df.index.map(self.link_map)
        df['fmt_tag'] = fmt_tag
        # save and order index
        ordered_index = utils.order_paths(df.index)
        return df, ordered_index
