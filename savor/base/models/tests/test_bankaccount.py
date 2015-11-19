import datetime

from django.conf import settings
from django.test import TestCase
from base.models import Cashflow
from core.gl.models import Account, Company, Counterparty, ExternalAccount

class CashflowTestCase(TestCase):
    def setUp(self):
        # Create a company for the expense
        self.default_company = Company(name="TEST_COMPANY", id="TEST")
        self.default_company.save()

        # Create accounts required to generate expense transactions
        ap = Account(id='3000', path="AP", display_name="AP")
        chk = Account(id='1001', path="CHECKING1", display_name="CHECKING1")
        
        ap.save()
        chk.save()
        
        cp1 = Counterparty(id='jpmc', name="Test C/P")
        cp1.save()

        Counterparty(id='test_cp', name="Test C/P").save()
        ExternalAccount(company=self.default_company, gl_account=chk, counterparty=cp1, label='CHK', name='Checking').save()
        


    def test_get_gl_transactions_checking(self):
        trans = Cashflow(ext_account=ExternalAccount.objects.get(label='CHK'), post_date=datetime.date(2015,1,1), description='test',
                        trans_type=Account.objects.get(id='3000'), amount='100.2', 
                        counterparty=Counterparty.objects.get(id='test_cp'))
        
        transactions = trans.get_gl_transactions()
        self.assertEqual(len(transactions), 1)
        lines = transactions[0]['lines']
        self.assertEqual(len(lines), 2)
        
        self.assertEqual(set([(Account.objects.get(id=1001), 100.2, Counterparty.objects.get(id='jpmc')), 
                                (Account.objects.get(id=3000), -100.2, Counterparty.objects.get(id='test_cp'))]), set(lines))
        