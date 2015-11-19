import datetime

from django.conf import settings
from django.test import TestCase
from base.models import Revolver
from core.gl.models import Account, Company, Counterparty

class RevolverTestCase(TestCase):
    def setUp(self):
        # Create a company for the expense
        self.default_company = Company(name="TEST_COMPANY", id="TEST")
        self.default_company.save()

        # Create accounts required to generate expense transactions
        
        Account(id='7001', path="expense", display_name="EXPENSE").save()
        Account(id='3250', path="revolver", display_name="REVOLVER").save()
        

    def test_get_gl_transactions_revolver(self):

        cp = Counterparty(id='test_cp', name="Test C/P")
        cp.save()

        trans = Revolver(company=self.default_company, date=datetime.date(2015,1,1), amount='100', counterparty=cp,
                        draw_type=Account.objects.get(id='7001'))
        transactions = trans.get_gl_transactions()

        self.assertEqual(len(transactions), 1)
