from behave import *
from dateutil.parser import parse
from decimal import Decimal

from base.models import Expense

import logging
logger = logging.getLogger('default')


@given(u'a new expense')
def impl(context):
    row = context.table[0]

    context.bmo = Expense(company_id=row['company'],
                          amount=Decimal(row['amount']),
                          account_id=row['account'],
                          expense_date=row['expense_date'],
                          start_date=row.get('start_date', row['expense_date']),
                          end_date=row.get('end_date', None),
                          counterparty_id=row['counterparty'],
                          paid_from_id=row['paid_from'])
