from behave import *
from decimal import Decimal
from hamcrest import assert_that, equal_to
import logging

logger = logging.getLogger('default')

@when(u'we calculate the BMO GL entries')
def impl(context):
    gl_entries = []
    for t in context.bmo.get_gl_transactions():
        lines = t.get('lines', [])
        new_lines = []
        for l in lines:
            new_line = (l[0], l[1], l[2], t['date'], t.get('date_end', None))
            new_lines.append(new_line)
        gl_entries += new_lines

    context.gl_entries = [(row[0].id,
                           Decimal(str(row[1])),
                           row[2].id,
                           row[3],
                           row[4]
                           ) for row in gl_entries]


@then(u'the lines should be')
def impl(context):
    expected = [(row['account'],
                 Decimal(row['amount']),
                 row['counterparty'],
                 row['date'],
                 None if row['date_end']=='' else row['date_end'])
                for row in context.table]
    assert_that(set(expected), equal_to(set(context.gl_entries)))