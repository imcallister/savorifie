import csv
import datetime

from django.core.management import call_command
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

import base.models


@login_required
def dump_fixtures(request):
    output = StringIO()

    call_command('dumpdata', 'auth.group', 'auth.user', 'gl.company', 'gl.department', 'gl.employee', 'gl.counterparty',
                 'gl.account', 'gl.externalaccount', 'environment', 'audit', 'reporting', 'base','--indent=2', stdout=output)
    data = output.getvalue()
    output.close()

    file_label = 'fixtures_%s' % datetime.datetime.now().strftime('%d-%b-%Y_%H-%M')
    response = HttpResponse(data, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=%s' % file_label
    return response


@login_required
def output_expenses(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)

    all_expenses = base.models.Expense.objects.all()
    header_row = [unicode(x).encode('utf-8') for x in all_expenses[0].__dict__.keys()]

    writer.writerow(header_row)
    for ex in all_expenses:
        line = [unicode(x).encode('utf-8') for x in ex.__dict__.values()]
        writer.writerow(line)
    return response
