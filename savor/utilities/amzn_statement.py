import os
import pandas as pd
from dateutil.parser import parse
from decimal import Decimal


class AmazonStatement(object):

	def __init__(self, path, file_name):
		self.data = pd.read_csv(os.path.join(path, file_name), delimiter='\t')
		self.data.fillna
		self.data['deposit-date'] = self.data['deposit-date'].fillna(method='ffill')
		self.data['deposit-date'] = self.data['deposit-date'].map(lambda x: parse(x).date())

	def amount_types(self):
		 return list(set(self.data['amount-type'].dropna().values))

	def amount_by_order(self):
		return self.data[['order-id', 'amount']].groupby('order-id').sum()

	def amount_by_type(self):
		return self.data[['amount-type', 'amount']].groupby('amount-typea').sum()

	def create_upload_file(self):
		amounts = self.data[['amount-type', 'order-id','amount']].dropna()
		amounts['amount'] = amounts['amount'].map(lambda x: Decimal(int(x * 100)) * Decimal('0.01'))
		gross = amounts[amounts['amount-type']=='ItemPrice'][['order-id', 'amount']].groupby('order-id').sum()['amount']

		fee_types = ['other-transaction', 'Promotion', 'ItemFees']
		fees = amounts[amounts['amount-type'].isin(fee_types)][['order-id', 'amount']].groupby('order-id').sum()['amount']
		net = amounts[['order-id', 'amount']].groupby('order-id').sum()['amount']

		payout_date = self.data.iloc[0]['deposit-date']

		upload_file = pd.DataFrame({'Payout Date': payout_date, 'Amount': gross, 'Fees': fees, 'Net': net, 'PaidThru': 'AMZN'})
		upload_file.index.name = 'Order'
		return upload_file
