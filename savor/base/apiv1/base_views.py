import datetime
import json
from dateutil.parser import parse
import pytz
from multipledispatch import dispatch

from savor.base.models import CreditCardTrans, Cashflow


EASTERN = pytz.timezone('US/Eastern')


@dispatch(dict)
def creditcardtrans(qstring):
    return list(CreditCardTrans.objects.order_by('id').values())


@dispatch(str, dict)
def creditcardtrans(cc_id, qstring):
    try:
        return CreditCardTrans.objects.filter(id=cc_id).first().values()
    except:
        return None

@dispatch(dict)
def cashflow(qstring):
    return list(Cashflow.objects.order_by('id').values())


@dispatch(str, dict)
def cashflow(cf_id, qstring):
    try:
        return Cashflow.objects.filter(id=cf_id).first().values()
    except:
        return None


def get_expense_data(expense, flds):
    data = dict((fld, getattr(expense, fld)) for fld in flds)
    return data

def model_changes(model_type, qstring):
    dt = qstring.get('date', datetime.datetime.now().date())
    if type(dt) != datetime.date:
        dt = parse(dt).date()
    
    if model_type == 'expense':
        return base.expense.get_changed(dt)
    elif model_type == 'nominal':
        return base.nominal.get_changed(dt)
    else:
        return


def nominal_changes(qstring):
    """
    shows changes made to nominal transactions since 'cutoff'
    """
    dt = qstring.get('cutoff', datetime.datetime.now().date())
    if type(dt) != datetime.date:
        dt = parse(dt).date()
    
    cutoff = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=EASTERN)

    all_nominal_history = [nom.history.get_queryset() for nom in NominalTransaction.objects.all()]
    qs_list = [h[0] for h in all_nominal_history if len(h)>0]
    history = [nom.__dict__ for nom in qs_list if nom.history_user_id and nom.history_date > cutoff]

    cols = ['comment', 'history_type', 'date_end', 'company_id', 'object_id', 'history_user_id', 'date', 'history_id', 'id', 'history_date']
    return [dict((k,str(v)) for k,v in nom.iteritems() if k in cols) for nom in history]
    

def expense_changes(qstring):
    dt = qstring.get('cutoff', datetime.datetime.now().date())
    if type(dt) != datetime.date:
        dt = parse(dt).date()
    
    cutoff = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=EASTERN)

    all_expense_history = [exp.history.get_queryset() for exp in Expense.objects.all()]
    qs_list = [h[0] for h in all_expense_history if len(h)>0]
    history = [exp.__dict__ for exp in qs_list if exp.history_user_id and exp.history_date > cutoff]

    cols = ['comment', 'last_name', 'process_date', 'id',  'first_name', 'employee_id', 'dept_name', 'company_id', 'expense_date', 
            'history_date', 'start_date', 'department_id', 'glcode', 'expense_report_name', 'vendor', 'end_date', 'history_id', 
            'approver', 'ccard', 'dept_code', 'expense_category', 'reason', 'history_type', 'reimbursable', 'counterparty_id', 
            'paid_from_id', 'e_mail', 'history_user_id', 'amount', 'processor']

    return [dict((k,str(v)) for k,v in exp.iteritems() if k in cols) for exp in history]

def large_expenses(qstring):
    threshold = 500
    dt = qstring.get('date', datetime.datetime.now().date())
    if type(dt) != datetime.date:
        dt = parse(dt).date()

    lg_expenses = Expense.objects.filter(expense_date__year=dt.year, expense_date__month=dt.month)\
                                      .filter(amount__gte=threshold) \
                                      .exclude(counterparty__id__in=['salesent','salestravel','salesaccom'])

    flds = ['id', 'expense_date','counterparty_name','start_date','end_date', 'amount_fmt', 'expense_report_name']
    return [get_expense_data(expense, flds) for expense in lg_expenses]


def month_nominals(qstring):
    dt = qstring.get('date', datetime.datetime.now().date())
    if type(dt) != datetime.date:
        dt = parse(dt).date()
    
    all_nominal = NominalTransaction.objects.filter(date__year=dt.year, date__month=dt.month)

    flds = ['date','comment','account0','amount0','account1','amount1']
    return [get_expense_data(expense, flds) for expense in nonESA_nominal]

