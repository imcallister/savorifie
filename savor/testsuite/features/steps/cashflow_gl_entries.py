from behave import *
from hamcrest import *
from decimal import Decimal

from accountifie.gl.factories import *
from base.models import Cashflow
from accountifie.gl.models import ExternalAccount, Account




@when(u'a new cashflow from "{ext_acct}" and "{amount}" and "{post_date}" and "{cp}"')
def impl(context, ext_acct, amount, post_date, cp):
    context.cashflow = Cashflow(ext_account=ExternalAccount.objects.get(label=ext_acct),
                                post_date=post_date,
                                description='test',
                                trans_type_id='3000',
                                amount=amount,
                                counterparty_id=cp)


@then(u'I see "{num_lines}" GL lines')
def impl(context, num_lines):
    assert_that(len(context.cashflow.get_gl_transactions()[0]['lines']), equal_to(int(num_lines)))


@given(u'a new cashflow')
def impl(context):
    row = context.table[0]
    context.bmo = Cashflow(ext_account=ExternalAccount.objects.get(label=row['ext_account']),
                           post_date=row['post_date'],
                           description='test',
                           trans_type_id='3000',
                           amount=row['amount'],
                           counterparty_id=row['counterparty'])

