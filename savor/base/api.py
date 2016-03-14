import datetime
import json
from dateutil.parser import parse
import pytz

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from .models import NominalTransaction, Expense


EASTERN = pytz.timezone('US/Eastern')


def get(api_view, params):
    return globals()[api_view](params)


def get_expense_data(expense, flds):
    data = dict((fld, getattr(expense, fld)) for fld in flds)
    return data


def get_nom_changes(dt):
    cutoff = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=EASTERN)
    qs_list = [nom.history.get_queryset()[0] for nom in NominalTransaction.objects.all()]
    history = [nom.__dict__ for nom in qs_list if nom.history_user_id and nom.history_date > cutoff]

    cols = ['comment', 'history_type', 'date_end', 'company_id', 'object_id', 'history_user_id', 'date', 'history_id', 'id', 'history_date']

    return [dict((k,str(v)) for k,v in nom.iteritems() if k in cols) for nom in history]
    
def get_exp_changes(dt):
    cutoff = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=EASTERN)
    qs_list = [exp.history.get_queryset()[0] for exp in Expense.objects.all()]
    history = [exp.__dict__ for exp in qs_list if exp.history_user_id and exp.history_date > cutoff]
    cols = ['comment', 'last_name', 'process_date', 'id',  'first_name', 'employee_id', 'dept_name', 'company_id', 'expense_date', 
            'history_date', 'start_date', 'department_id', 'glcode', 'expense_report_name', 'vendor', 'end_date', 'history_id', 
            'approver', 'ccard', 'dept_code', 'expense_category', 'reason', 'history_type', 'reimbursable', 'counterparty_id', 
            'paid_from_id', 'e_mail', 'history_user_id', 'amount', 'processor']

    return [dict((k,str(v)) for k,v in exp.iteritems() if k in cols) for exp in history]

def model_changes(request, model_type):
    dt = parse(request.GET['date']).date()
    
    if model_type == 'expense':
        return HttpResponse(json.dumps(get_exp_changes(dt), cls=DjangoJSONEncoder), content_type="application/json")
    elif model_type == 'nominal':
        return HttpResponse(json.dumps(get_nom_changes(dt), cls=DjangoJSONEncoder), content_type="application/json")
    else:
        return HttpResponse(json.dumps('unknown model_type'))


def large_expenses(query_dict):
    threshold = 500
    dt = parse(query_dict.get('date')).date()
    lg_expenses = Expense.objects.filter(expense_date__year=dt.year, expense_date__month=dt.month)\
                                      .filter(amount__gte=threshold) \
                                      .exclude(counterparty__id__in=['salesent','salestravel','salesaccom'])

    flds = ['id', 'expense_date','counterparty_name','start_date','end_date', 'amount_fmt', 'expense_report_name']
    return [get_expense_data(expense, flds) for expense in lg_expenses]


def nominal(query_dict):
    dt = parse(query_dict.get('date')).date()
    all_nominal = NominalTransaction.objects.filter(date__year=dt.year, date__month=dt.month)

    flds = ['date','comment','account0','amount0','account1','amount1']
    return [get_expense_data(expense, flds) for expense in all_nominal]
