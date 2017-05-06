from behave import given

from accountifie.gl.factories import CompanyFactory, AccountFactory, CounterpartyFactory, ExternalAccountFactory
from accountifie.environment.models import Variable

import logging
logger = logging.getLogger('default')


@given(u'there are companies')
def impl(context):
    companies = [CompanyFactory(id=row['id'],
                                name=row['name'],
                                cmpy_type=row['cmpy_type']) for row in context.table]

@given('there are accounts')
def impl(context):
    accounts = [AccountFactory(id=row['id'],
                               path=row['path']) for row in context.table]


@given(u'there are counterparties')
def impl(context):
    counterparties = [CounterpartyFactory(id=row['id']) for row in context.table]


@given(u'there are external accounts')
def impl(context):
    externalaccounts = [ExternalAccountFactory(company_id=row['company'],
                                               gl_account_id=row['account_id'],
                                               counterparty_id=row['cp'],
                                               label=row['account_id'],
                                               name=row['account_id']) for row in context.table]

@given(u'there are environment variables')
def impl(context):
    for row in context.table:
        Variable(key=row['key'], value=row['value']).save()
