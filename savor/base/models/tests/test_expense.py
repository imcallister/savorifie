import datetime
from decimal import Decimal
from django.conf import settings
from django.test import TestCase
from base.models import Expense
from accountifie.gl.models import Account, Company, Counterparty
from accountifie.environment.models import Variable

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
        Account(id='7890', path="EXPENSE.TEST", display_name="Expense Test").save()

        Counterparty(id='testcp1', name="test1").save()



    def test_get_gl_transactions_happy_path(self):
        expense = Expense(company=self.default_company,
                          amount='123.45',
                          account_id='7890',
                          counterparty_id='testcp1')

        transactions = expense.get_gl_transactions()

        self.assertEqual(len(transactions), 1)
        lines = set((l[0].id, l[1], l[2].id) for l in transactions[0]['lines'])
        self.assertEqual(len(lines), 2)

        should_be = [('7890', Decimal('123.45'), 'testcp1'),
                     ('3000', Decimal('-123.45'), 'testcp1')]

        self.assertEqual(set(should_be), set(lines))


    def test_get_gl_transactions_multiperiod_small(self):
        expense = Expense(company=self.default_company,
                          amount='123.45',
                          account_id='7890',
                          start_date=datetime.date(2015,1,1),
                          end_date=datetime.date(2015,10,1),
                          counterparty_id='testcp1')

        transactions = expense.get_gl_transactions()

        self.assertEqual(len(transactions), 1)
        lines = set((l[0].id, l[1], l[2].id) for l in transactions[0]['lines'])
        self.assertEqual(len(lines), 2)

        should_be = [('7890', Decimal('123.45'), 'testcp1'),
                     ('3000', Decimal('-123.45'), 'testcp1')]

        self.assertEqual(set(should_be), set(lines))


    def test_get_gl_transactions_multiperiod_exp_at_end(self):
        expense = Expense(company=self.default_company,
                          amount=Decimal('1230.45'),
                          account_id='7890',
                          start_date=datetime.date(2015,1,1),
                          end_date=datetime.date(2015,10,1),
                          expense_date=datetime.date(2015,10,1),
                          counterparty_id='testcp1')

        transactions = expense.get_gl_transactions()

        self.assertEqual(len(transactions), 2)
        lines = set((l[0].id, l[1], l[2].id) for l in transactions[0]['lines'])
        self.assertEqual(len(lines), 4)

        should_be = [('7890', Decimal('1230.45'), 'testcp1'),
                     ('3000', Decimal('-1230.45'), 'testcp1'),
                     ('3110', Decimal('-1230.45'), 'testcp1'),
                     ('7890', Decimal('1230.45'), 'testcp1')]

        self.assertEqual(set(should_be), set(lines))


    def test_get_gl_transactions_multiperiod_exp_at_start(self):
        expense = Expense(company=self.default_company,
                          amount=Decimal('1230.45'),
                          account_id='7890',
                          start_date=datetime.date(2015,1,1),
                          end_date=datetime.date(2015,10,1),
                          expense_date=datetime.date(2015,1,1),
                          counterparty_id='testcp1')
        transactions = expense.get_gl_transactions()

        self.assertEqual(len(transactions), 2)
        lines_0 = set((l[0].id, l[1], l[2].id) for l in transactions[0]['lines'])
        lines_1 = set((l[0].id, l[1], l[2].id) for l in transactions[1]['lines'])
        lines = lines_0 + lines_1
        self.assertEqual(len(lines), 4)

        should_be = [('1250', Decimal('1230.45'), 'testcp1'),
                     ('3000', Decimal('-1230.45'), 'testcp1'),
                     ('1250', Decimal('-1230.45'), 'testcp1'),
                     ('7890', Decimal('1230.45'), 'testcp1')]
        
        self.assertEqual(set(should_be), set(lines))
