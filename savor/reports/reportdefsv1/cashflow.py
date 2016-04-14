import datetime
import pandas as pd
from dateutil.parser import parse
import numpy as np

from accountifie.reporting.models import Report, BasicBand, TextBand
from accountifie.toolkit.utils import DZERO
import accountifie.toolkit.utils as utils


class Cashflow(Report):
    
    def __init__(self, company_id, date=None):

        self.date = date
        self.description = 'Statement of Cash Flows'
        self.title = None
        self.company_id = company_id
        self.columns = {}
        self.column_order = []
        self.set_company()
        self.calc_type = 'diff'
        self.label_map = utils.get_alias
        self.link_map = utils.path_history_link
    
        self.works_for = ['SAV']
    
    def calcs(self):
        table_data = []
        path_totals = {}

        header = {'fmt_tag': 'header', 'label': 'CASHFLOWS FROM OPERATING ACTIVITIES'}
        table_data.append(header)

        # operating activities cashflows
        op_paths = ['equity.retearnings', 
                'liabilities.curr.accinterest',
                'equity.retearnings.opexp.depamort',
                'assets.curr.other.prepaidtax',
                'assets.curr.other.prepaidexp',
                'assets.curr.rec',
                'assets.curr.acc',
                'assets.curr.deposit',
                'assets.noncurr.secdeposits',
                'liabilities.curr',
                'liabilities.noncurr.other',
                ]

        net_cash = self.query_manager.pd_path_balances(self.company_id, self.columns, op_paths)
        if 'equity.retearnings.opexp.depamort' in net_cash.index:
            net_cash.loc['equity.retearnings.opexp.depamort'] = net_cash.loc['equity.retearnings.opexp.depamort'] * (-1.0)

        net_cash['fmt_tag'] = 'item'
        net_cash['label'] = net_cash.index.map(self.label_map)
        net_cash['link'] = net_cash.index.map(self.link_map)

        net_cash.loc['net_cash'] = net_cash[self.column_order].sum()
        path_totals['op'] = net_cash.loc['net_cash'].copy()
        net_cash.loc['net_cash', 'fmt_tag'] = 'minor_total'
        net_cash.loc['net_cash', 'label'] = 'Net cash provided by operating activities'
        net_cash.loc['net_cash', 'link'] = ''
        

        table_data += net_cash.to_dict(orient='records')

        header = {'fmt_tag': 'header', 'label': 'CASHFLOWS FROM INVESTING ACTIVITIES'}
        table_data.append(header)
        
        # investing activities cashflows
        inv_paths = ['assets.noncurr.premandequip', 
                'assets.intang.capsoftware',
                'assets.noncurr.invest',
                'assets.noncurr.subloan',
                'assets.curr.accinterest'
                
                ]
        inv_cash = self.query_manager.pd_path_balances(self.company_id, self.columns, inv_paths)
        try:
            equip_adj = self.query_manager.pd_path_balances(self.company_id, self.columns, ['equity.retearnings.opexp.depamort.premandequip']).loc['equity.retearnings.opexp.depamort.premandequip'] 
            inv_cash.loc['assets.noncurr.premandequip'] = inv_cash.loc['assets.noncurr.premandequip'] + equip_adj
        except:
            pass

        try:
            software_adj = self.query_manager.pd_path_balances(self.company_id, self.columns, ['equity.retearnings.opexp.depamort.software']).loc['equity.retearnings.opexp.depamort.software']
            inv_cash.loc['assets.intang.capsoftware'] = inv_cash.loc['assets.intang.capsoftware'] + software_adj
        except:
            pass
        
        #if not inv_cash.empty:
        inv_cash['fmt_tag'] = 'item'
        inv_cash['label'] = inv_cash.index.map(self.label_map)
        inv_cash['link'] = inv_cash.index.map(self.link_map)


        inv_cash.loc['inv_cash'] = inv_cash[self.column_order].apply(lambda x: sum(x), axis=0).fillna(DZERO)
        path_totals['inv'] = inv_cash.loc['inv_cash'].copy()
        inv_cash.loc['inv_cash', 'fmt_tag'] = 'minor_total'
        inv_cash.loc['inv_cash', 'label'] = 'Net cash provided by investing activities'
        inv_cash.loc['inv_cash', 'link'] = ''
        
        table_data += inv_cash.to_dict(orient='records')

        header = {'fmt_tag': 'header', 'label': 'CASHFLOWS FROM FINANCING ACTIVITIES'}
        table_data.append(header)
        
        # investing activities cashflows
        fin_paths = ['liabilities.noncurr.ltdebt', 
                'equity.commonstock',
                'equity.prefstock',
                'equity.membercontrib',
                'equity.apic'
                ]
        fin_cash = self.query_manager.pd_path_balances(self.company_id, self.columns, fin_paths)

        fin_cash['fmt_tag'] = 'item'
        fin_cash['label'] = fin_cash.index.map(self.label_map)
        fin_cash['link'] = fin_cash.index.map(self.link_map)

        fin_cash.loc['fin_cash'] = fin_cash[self.column_order].apply(lambda x: sum(x), axis=0).fillna(DZERO)
        path_totals['fin'] = fin_cash.loc['fin_cash'].copy()
        fin_cash.loc['fin_cash','fmt_tag'] = 'minor_total'
        fin_cash.loc['fin_cash','label'] = 'Net cash provided by financing activities'
        fin_cash.loc['fin_cash','link'] = ''
        
        table_data += fin_cash.to_dict(orient='records')

        net_cash = pd.DataFrame(path_totals).sum(axis=1).fillna(DZERO)
        net_cash['label'] = 'NET INCREASE IN CASH'
        net_cash['fmt_tag'] = 'major_total'
        net_cash['link'] = ''

        table_data.append(net_cash.to_dict())

        
        # custom ... cash and beginning and end and an asset band
        start_periods = {}
        for title in self.columns:
            period_tag = self.columns[title]
            start_periods[title] = utils.start_of_period(period_tag) - datetime.timedelta(days=1)

        end_periods = {}
        for title in self.columns:
            period_tag = self.columns[title]
            end_periods[title] = utils.end_of_period(period_tag)

        start_cashbal = self.query_manager.pd_path_balances(self.company_id, start_periods, ['assets.curr.cashandeq'], assets=True).loc['assets.curr.cashandeq']
        end_cashbal = self.query_manager.pd_path_balances(self.company_id, end_periods, ['assets.curr.cashandeq'], assets=True).loc['assets.curr.cashandeq']

        start_cashbal['fmt_tag'] = 'item'
        start_cashbal['label'] = 'Cash at start of period'
        start_cashbal['link'] = ''
        table_data.append(start_cashbal.to_dict())

        end_cashbal['fmt_tag'] = 'item'
        end_cashbal['label'] = 'Cash at end of period'
        end_cashbal['link'] = ''
        table_data.append(end_cashbal.to_dict())

        """
        check = cash_chg[self.column_order] - (end_cashbal[self.column_order] - start_cashbal[self.column_order])
        
        if any(x > 1.0 for x in check.values): 
            check['fmt_tag'] = 'warning'
            check['label'] = 'WARNING: Net Increase in Cash does not match'
            check['link'] = ''
            content += self.get_row(check)

        return content
        """

        for row in table_data:
            if row['fmt_tag'] != 'header':

                for col in self.column_order:
                    row[col] = {'text': row[col], 'link': row['link']}

        return table_data
