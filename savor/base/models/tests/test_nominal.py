import datetime

from django.conf import settings
from django.test import TestCase
from base.models import NominalTransaction, NominalTranLine
from core.gl.models import Account, Company, Counterparty
from core.environment.models import Variable

class NominalTestCase(TestCase):
    def setUp(self):
        # Create a company for the expense
        self.default_company = Company(name="TEST_COMPANY", id="TEST")
        self.default_company.save()

        # Create accounts required to generate expense transactions
        
        Variable(key='DEFAULT_COMPANY_ID', value='TEST').save()

    def test_get_gl_transactions_happy_path(self):
        nom_trans = NominalTransaction(id='98765',company=self.default_company, date=datetime.date(2015,1,1))
        
        debit = Account(id='7000', path='capital.opexp.retearnings.debit', display_name='7000')
        credit = Account(id='7010', path='capital.opexp.retearnings.credit', display_name='7010')
        debit.save()
        credit.save()

        cp = Counterparty(id='test_cp', name="Test C/P")
        cp.save()
        
        debit_line = NominalTranLine(transaction_id=nom_trans.id, account=debit, amount='123.4', counterparty=cp)
        debit_line.save()
        nom_trans.nominaltranline_set.add(debit_line)

        credit_line = NominalTranLine(transaction_id=nom_trans.id, account=credit, amount='-123.4', counterparty=cp)
        credit_line.save()
        nom_trans.nominaltranline_set.add(credit_line)

        transactions = nom_trans.get_gl_transactions()
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(len(transactions[0]['lines']), 2)