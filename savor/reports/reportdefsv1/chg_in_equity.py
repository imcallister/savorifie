import datetime
import copy
from decimal import Decimal
from collections import defaultdict
import pandas as pd
import numpy as np

from financifie.reporting.models import Report, BasicBand, TextBand
import financifie.gl.models
from _utils import DZERO, fmt
import _utils as utils
import reporting.stock_tables as stock_tables


COL_LABELS = {'start': "Shareholder Equity at Start of Period",
        'stockcomp': 'Common Stock Issued as Compensation',
        'prefstock': 'Series A-1 Preferred Shares',
        'othercommon': 'Other Common Stock Issued',
        'retearnings': 'Net Loss',
        'end': "Shareholder Equity at End of Period",
        'chg': 'Change in period'
        }

ITEM = {'css_class': 'minor', 'indent': 1, 'type': 'group_item'}
MINOR_TOTAL = {'css_class': 'minor', 'indent': 0, 'type': 'group_total'}
MAJOR_TOTAL = {'css_class': 'major', 'indent': 0, 'type': 'group_total2'}
WARNING = {'css_class': 'warning', 'indent': 0, 'type': 'normal'}

ROW_FORMATS = {'item': ITEM, 'minor_total': MINOR_TOTAL, 'major_total': MAJOR_TOTAL, 'warning': WARNING}


class ChgInEquityStatement(Report):
    def __init__(self, company_id, date=None):

        self.date = date
        self.dflt_title = "Statement of Changes in Shareholder Equity"
        self.description = self.dflt_title
        self.company_id = company_id
        self.columns = {'Preferred Par Value': 'equity.prefstock', 
                        'Preferred Shares': 'preferred_par',
                        'Common Par Value': 'equity.commonstock', 
                        'Common Shares': 'common_par',
                        'APIC': 'equity.apic', 
                        'Retained Earnings': 'equity.retearnings', 
                        'Total Shareholder Equity': 'Total'}
        
        self.column_order = ['Preferred Shares', 'Preferred Par Value', 'Common Shares', 'Common Par Value',
                                'APIC', 'Retained Earnings', 'Total Shareholder Equity']
        
        self.calc_type = 'as_of'
        self.set_company()
        self.works_for = ['SAV']

        self.link_map = lambda x: ''
        self.label_map = lambda x: COL_LABELS[x]
        self.dates = None
        

    
    def set_columns(self, columns, column_order=None):
        # columns are fixed... don't mistakenly adjust to dates
        pass

    def configure(self, as_of=None, col_tag=None, path=None):
        config = utils.config_fromcoltag(col_tag, self.description, self.calc_type)
        self.title = config['title']
        self.dates= config['columns']
        self.date_order = config['column_order']
        
    
    def calcs(self):
        table_data = []

        paths = ['equity.prefstock', 'equity.commonstock', 'equity.apic', 'equity.retearnings']
        
        start_col = self.date_order[0]
        end_col = self.date_order[2]
        chg_col = self.date_order[1]

        child_paths = []
        for path in ['equity.prefstock', 'equity.commonstock', 'equity.apic']:
            child_paths += financifie.gl.models.get_child_paths(path)

        top_df = self.query_manager.pd_path_balances(self.company_id, self.dates, paths)
        
        drill_df = self.query_manager.pd_path_balances(self.company_id, self.dates, child_paths)
        drill_df = drill_df[drill_df[chg_col] != DZERO] 
        output_df = top_df

        stockcomp = drill_df.index.map(lambda x: 0.0 if 'stockcomp' not in x else 1.0) * drill_df[chg_col]
        stockcomp = stockcomp[stockcomp != 0.0]
        stockcomp.index = stockcomp.index.map(lambda x: '.'.join(x.split('.')[:2]))
        
        othercommon = drill_df.index.map(lambda x: 0.0 if 'other' not in x else 1.0) * drill_df[chg_col]
        othercommon = othercommon[othercommon != 0.0]
        othercommon.index = othercommon.index.map(lambda x: '.'.join(x.split('.')[:2]))

        retearnings = top_df.index.map(lambda x: 0.0 if 'retearnings' not in x else 1.0) * top_df[chg_col]
        retearnings = retearnings[retearnings != 0.0]
        retearnings.index = retearnings.index.map(lambda x: '.'.join(x.split('.')[:2]))

        prefstock = drill_df.index.map(lambda x: 0.0 if 'prefstock' not in x else 1.0) * drill_df[chg_col]
        prefstock = prefstock[prefstock != 0.0]
        prefstock.index = prefstock.index.map(lambda x: '.'.join(x.split('.')[:2]))

        output_df['stockcomp'] = stockcomp
        output_df['othercommon'] = othercommon
        output_df['retearnings'] = retearnings
        output_df['prefstock'] = prefstock

        

        output_df.fillna(0.0, inplace=True)
        output_df.loc['Total'] = output_df.apply(sum, axis=0)

        
        chg_cols = [x for x in output_df.columns if x not in [start_col, end_col, chg_col]]
        check_band = output_df[chg_cols].apply(sum, axis=1).values - (output_df[end_col] - output_df[start_col])
        
        
        output_df.rename(columns={start_col: 'start', chg_col: 'chg', end_col: 'end'}, inplace=True)
        output_df = output_df.T
        output_df['fmt_tag'] = 'item'
        
        if 'equity.commonstock' not in output_df.columns:
            output_df['equity.commonstock'] = 0.0

        if 'equity.prefstock' not in output_df.columns:
            output_df['equity.prefstock'] = 0.0
        
        mapper = dict((v,k) for k,v in COL_LABELS.iteritems())
        table = stock_tables.stock_table(self.dates[start_col], self.dates[end_col])
 
        table.index = table.index.map(lambda x: mapper[x])        
        if 'common' in table.columns:
            output_df['common_par'] = table['common']
        else:
            output_df['common_par'] = 0.0

        if 'series_A1' in table.columns:
            output_df['preferred_par'] = table['series_A1']
        else:
            output_df['preferred_par'] = 0.0
        
        output_df.fillna(0.0, inplace=True)

        for row in ['start', 'end', 'chg']:
            output_df.loc[row, 'fmt_tag'] = 'minor_total'

        output_df['link'] = ''
        output_df['label'] = output_df.index.map(lambda x: COL_LABELS[x])

        
        for lbl in ['start','stockcomp', 'prefstock','othercommon', 'retearnings', 'end', 'chg']:
            table_data.append(output_df.loc[lbl].to_dict())
        
        for row in table_data:
            if row['fmt_tag'] != 'header':
                for col in [x for x in self.column_order if x in row]:
                    row[col] = {'text': row[self.columns[col]], 'link': row['link']}
        
        return table_data


    def get_row(self, df_row):
        used_cols = [x for x in self.column_order if self.columns[x] in df_row]

        if df_row['fmt_tag'] == 'header':
            return TextBand(df_row['label'], css_class='normal').get_rows(self)
        else:
            values = [utils.entry(df_row[self.columns[col_label]] , link='') for col_label in used_cols]
            fmt_tag = df_row['fmt_tag']
            _css_class = ROW_FORMATS[fmt_tag]['css_class']
            _indent  = ROW_FORMATS[fmt_tag]['indent']
            _type  = ROW_FORMATS[fmt_tag]['type']
            return BasicBand(df_row['label'], css_class=_css_class, values=values, indent=_indent, type=_type).get_rows(self)
