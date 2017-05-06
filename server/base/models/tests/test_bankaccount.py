import datetime

from django.conf import settings
from django.test import TestCase
from base.models import Cashflow
from accountifie.gl.models import Account, Company, Counterparty, ExternalAccount


class CashflowTestCase(TestCase):
    def setUp(self):
        # Create a company for the expense
        self.default_company = Company(name="TEST_COMPANY", id="TEST")
        self.default_company.save()

        # Create accounts required to generate expense transactions
        self.ap = Account(id='3000', path="AP", display_name="AP")
        self.chk = Account(id='1001', path="CHECKING1", display_name="CHECKING1")

        self.ap.save()
        self.chk.save()

        self.cp1 = Counterparty(id='jpmc', name="Test C/P")
        self.cp1.save()

        self.cp2 = Counterparty(id='test_cp', name="Test C/P")
        self.cp2.save()
        ExternalAccount(company=self.default_company, gl_account=self.chk, counterparty=self.cp1, label='CHK', name='Checking').save()


    def test_get_gl_transactions_checking(self):
        trans = Cashflow(ext_account=ExternalAccount.objects.get(label='CHK'),
                         post_date=datetime.date(2015,1,1), description='test',
                         trans_type=Account.objects.get(id='3000'), amount='100.2',
                         counterparty=Counterparty.objects.get(id='test_cp'))

        transactions = trans.get_gl_transactions()
        self.assertEqual(len(transactions), 1)
        lines = transactions[0]['lines']
        self.assertEqual(len(lines), 2)

        self.assertEqual(set([(self.chk, 100.2, self.cp1),
                              (self.ap, -100.2, self.cp2)]),
                         set(lines))
