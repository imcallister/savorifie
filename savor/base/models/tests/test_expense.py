import datetime
from decimal import Decimal
from django.conf import settings
from django.test import TestCase
from base.models import Expense
from core.gl.models import Account, Company
from core.environment.models import Variable

class ExpenseTestCase(TestCase):
    def setUp(self):
        # Create a company for the expense
        self.default_company = Company(name="TEST_COMPANY", id="TEST")
        self.default_company.save()

        Variable(key='GL_ACCOUNTS_PAYABLE', value='3000').save()
        Variable(key='GL_PREPAID_EXP', value='1250').save()
        Variable(key='GL_ACCRUED_LIAB', value='3110').save()

        # Create accounts required to generate expense transactions
        Account(id='3000', path="GL_ACCOUNTS_PAYABLE", display_name="GL_ACCOUNTS_PAYABLE").save()
        Account(id='1250', path="GL_PREPAID_EXP", display_name="GL_PREPAID_EXP").save()
        Account(id='3110', path="GL_ACCRUED_LIAB", display_name="GL_ACCRUED_LIAB").save()

    def test_get_gl_transactions_happy_path(self):
        expense = Expense(company=self.default_company, amount=123.45, glcode='2345-0000-000')
        transactions = expense.get_gl_transactions()

        self.assertEqual(len(transactions), 1)
        lines = transactions[0]['lines']
        self.assertEqual(len(lines), 2)
        self.assertEqual(set([(Account.objects.get(id=2345), 123.45, None), (Account.objects.get(id=3000), -123.45, None)]), set(lines))


        
    def test_get_gl_transactions_multiperiod_small(self):
        expense = Expense(company=self.default_company, amount=123.45, glcode='2345-0000-000',
                            start_date=datetime.date(2015,1,1), end_date=datetime.date(2015,10,1))
        transactions = expense.get_gl_transactions()

        self.assertEqual(len(transactions), 1)
        lines = transactions[0]['lines']
        self.assertEqual(len(lines), 2)
        self.assertEqual(set([(Account.objects.get(id=2345), 123.45, None), (Account.objects.get(id=3000), -123.45, None)]), set(lines))

    def test_get_gl_transactions_multiperiod_exp_at_end(self):
        expense = Expense(company=self.default_company, amount=Decimal('1230.45'), glcode='2345-0000-000',
                            start_date=datetime.date(2015,1,1), end_date=datetime.date(2015,10,1), expense_date=datetime.date(2015,10,1))
        transactions = expense.get_gl_transactions()

        self.assertEqual(len(transactions), 2)
        lines = transactions[0]['lines'] + transactions[1]['lines']
        self.assertEqual(len(lines), 4)

        expected = [(Account.objects.get(id=3110), Decimal('1230.45'), None), (Account.objects.get(id=3000), Decimal('-1230.45'), None),
                    (Account.objects.get(id=3110), Decimal('-1230.45'), None), (Account.objects.get(id=2345), Decimal('1230.45'), None)]
        self.assertEqual(set(expected), set(lines))

    def test_get_gl_transactions_multiperiod_exp_at_start(self):
        expense = Expense(company=self.default_company, amount=Decimal('1230.45'), glcode='2345-0000-000',
                            start_date=datetime.date(2015,1,1), end_date=datetime.date(2015,10,1), expense_date=datetime.date(2015,1,1))
        transactions = expense.get_gl_transactions()

        self.assertEqual(len(transactions), 2)
        lines = transactions[0]['lines'] + transactions[1]['lines']
        self.assertEqual(len(lines), 4)

        expected = [(Account.objects.get(id=1250), Decimal('1230.45'), None), (Account.objects.get(id=3000), Decimal('-1230.45'), None),
                    (Account.objects.get(id=1250), Decimal('-1230.45'), None), (Account.objects.get(id=2345), Decimal('1230.45'), None)]
        self.assertEqual(set(expected), set(lines))
