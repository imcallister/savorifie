import pytz
from decimal import Decimal
from dateutil.parser import parse
import datetime

import pandas as pd

import tables
import models as audit
from .forms import CommentForm


EASTERN = pytz.timezone('US/Eastern')
UTC = pytz.timezone('UTC')

def parse_time(row, date_col, time_col):
    try:
        return  EASTERN.localize(parse('%s %s' %(row[date_col], row[time_col])))
    except:
        return None

def parse_datetime(x):
    if pd.isnull(x):
        return None
    try:
        return parse(x)
    except:
        return None

def parse_decimal(x):
    if pd.isnull(x):
        return None
    if x is not None:
        return Decimal(str(x).replace(',',''))
    return None


def prep_task_views(request, id=None):
    context = {}
    qs = request.GET.copy()
    form_type = None if not(qs) else qs.pop('form_type', '')[0]
    task_id = id
    context['task_id'] = task_id
    task = audit.Task.objects.get(id=task_id)
    context['date'] = datetime.datetime.strftime(task.as_of, '%d-%b-%Y')
    user = request.user
    context['user'] = user
    context['status'] = task.status_tag
    
    context['audit_trail'] = tables.bstrap_tables.task_audit(task_id)
    context['comment_form'] = CommentForm()
    return task, user, context, qs, form_type