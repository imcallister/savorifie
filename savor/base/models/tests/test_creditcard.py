import datetime

from django.conf import settings
from django.test import TestCase
from base.models import Mcard
from core.gl.models import Account, Company, Counterparty
from core.environment.models import Variable

class McardTestCase(TestCase):
    def setUp(self):
        # Create a company for the expense
        self.default_company = Company(name="TEST_COMPANY", id="TEST")
        self.default_company.save()

        Variable(key='GL_ACCOUNTS_PAYABLE', value='3000').save()
        # Create accounts required to generate expense transactions
        Account(id='3000', path="GL_ACCOUNTS_PAYABLE", display_name="GL_ACCOUNTS_PAYABLE").save()
        Account(id='3021', path="mastercard", display_name="Mastercard").save()

        Counterparty(id='mastercard', name="Test C/P").save()


    def test_get_gl_transactions_happy_path(self):

        cp = Counterparty(id='test_cp', name="Test C/P")
        cp.save()

        trans = Mcard(company=self.default_company, trans_date=datetime.date(2015,1,1), type='sale', amount='100', counterparty=cp)
        transactions = trans.get_gl_transactions()

        self.assertEqual(len(transactions), 1)
