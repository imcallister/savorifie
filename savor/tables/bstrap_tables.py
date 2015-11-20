from django.template import Context
from django.template.loader import get_template

from accountifie._utils import get_default_company


def get_bstrap_table(data_url, row_defs, pagination="true", pagination_num=25):
    context = {}

    context['data_url'] = data_url
    context['row_defs'] = row_defs
    context['pagination'] = pagination
    context['pagination_num'] = pagination_num

    tmpl = get_template('bstrap_table.html')
    return tmpl.render(Context(context))


def daily_activity(dt):
    data_url = "/reporting/reports/AccountActivity/?col_tag=daily_%s&format=json" % dt.isoformat()
    row_defs = [{'data_field': 'label', 'value': 'Account', 'formatter': 'nameFormatter'},
                {'data_field': 'Yesterday', 'value': 'Yesterday', 'formatter': 'drillFormatter'},
                {'data_field': 'Change', 'value': 'Change', 'formatter': 'drillFormatter'},
                {'data_field': 'Today', 'value': 'Today', 'formatter': 'drillFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def large_expenses(dt):
    data_url = "/base/api/large_expenses/?date=%s&company=%s" % (dt, get_default_company())
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'expense_date', 'value': 'Expense Date', 'formatter': 'nameFormatter'},
                {'data_field': 'counterparty_name', 'value': 'Vendor', 'formatter': 'nameFormatter'},
                {'data_field': 'start_date', 'value': 'Expense Start', 'formatter': 'nameFormatter'},
                {'data_field': 'end_date', 'value': 'Expense End', 'formatter': 'nameFormatter'},
                {'data_field': 'amount_fmt', 'value': 'Amount', 'formatter': 'nameFormatter'},
                {'data_field': 'expense_report_name', 'value': 'Expense Report', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def nominal(dt):
    if type(dt) == str:
        dt_str = dt
    else:
        dt_str = dt.isoformat()

    data_url = "/base/api/nominal/?date=%s" % dt_str
    row_defs = [{'data_field': 'date', 'value': 'Date', 'formatter': 'nameFormatter'},
                {'data_field': 'comment', 'value': 'Comment', 'formatter': 'nameFormatter'},
                {'data_field': 'account0', 'value': 'Account1', 'formatter': 'nameFormatter'},
                {'data_field': 'amount0', 'value': 'Amount1', 'formatter': 'nameFormatter'},
                {'data_field': 'account1', 'value': 'Account2', 'formatter': 'nameFormatter'},
                {'data_field': 'amount1', 'value': 'Amount2', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def balance_trends(dt, acct_list=None, accts_path=None, company_id=get_default_company()):
    if acct_list:
        data_url = "/reporting/api/balance_trends/?date=%s&acct_list=%s&company_id=%s" %( dt, '.'.join(acct_list), company_id)
    elif accts_path:
        data_url = "/reporting/api/balance_trends/?date=%s&accts_path=%s&company_id=%s" %( dt, accts_path, company_id)

    row_defs = [{'data_field': 'label', 'value': 'Date', 'formatter': 'nameFormatter'},
                {'data_field': 'M_2', 'value': '2 Months Ago', 'formatter': 'drillFormatter'},
                {'data_field': 'M_1', 'value': '1 Month Ago', 'formatter': 'drillFormatter'},
                {'data_field': 'M_0', 'value': 'This Month', 'formatter': 'drillFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def nominal_changes(dt):
    data_url = "/base/api/changes/nominal/?date=%s" % dt.isoformat()
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'company_id', 'value': 'Company', 'formatter': 'nameFormatter'},
                {'data_field': 'history_type', 'value': 'Change', 'formatter': 'nameFormatter'},
                {'data_field': 'comment', 'value': 'Comment', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def expense_changes(dt):
    data_url = "/base/api/changes/expense/?date=%s" % dt.isoformat()
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'start_date', 'value': 'Start Date', 'formatter': 'nameFormatter'},
                {'data_field': 'glcode', 'value': 'GL Account', 'formatter': 'nameFormatter'},
                {'data_field': 'glcode', 'value': 'GL Account Name', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def check_external_bals(dt, company_id=get_default_company()):
    data_url = "/gl/api/check_external_bals/?date=%s&company_id=%s" % (dt.isoformat(), company_id)
    row_defs = [{'data_field': 'Account', 'value': 'Account', 'formatter': 'nameFormatter'},
                {'data_field': 'Internal', 'value': 'Internal', 'formatter': 'valueFormatter'},
                {'data_field': 'External', 'value': 'External', 'formatter': 'valueFormatter'},
                {'data_field': 'Diff', 'value': 'Diff', 'formatter': 'valueFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def external_bals_history(dt, company_id=get_default_company(), acct=''):
    data_url = "/gl/api/external_bals_history/?date=%s&company_id=%s&acct=%s" % (dt.isoformat(), company_id, acct)
    row_defs = [{'data_field': 'Date', 'value': 'Date', 'formatter': 'nameFormatter'},
                {'data_field': 'Internal', 'value': 'Internal', 'formatter': 'valueFormatter'},
                {'data_field': 'External', 'value': 'External', 'formatter': 'valueFormatter'},
                {'data_field': 'Diff', 'value': 'Diff', 'formatter': 'valueFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def tasks():
    data_url = 'api/tasks_list/'
    row_defs = [{'data_field': 'id_link', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'status_tag', 'value': 'Status', 'formatter': 'nameFormatter'},
                {'data_field': 'task_def', 'value': 'Task Def', 'formatter': 'nameFormatter'},
                {'data_field': 'as_of', 'value': 'Date', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def task_defs():
    data_url = '/audit/api/task_defs/'
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'desc', 'value': 'Description', 'formatter': 'nameFormatter'},
                {'data_field': 'freq', 'value': 'Freqiency', 'formatter': 'nameFormatter'},
                {'data_field': 'approvers', 'value': 'Approvers', 'formatter': 'nameFormatter'},
                {'data_field': 'preparers', 'value': 'Preparers', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def audit_trail():
    data_url = '/audit/api/audit_trail/'
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'timestamp', 'value': 'Timestamp', 'formatter': 'nameFormatter'},
                {'data_field': 'desc', 'value': 'Description', 'formatter': 'nameFormatter'},
                {'data_field': 'comment_fmt', 'value': 'Comment', 'formatter': 'nameFormatter'},
                {'data_field': 'task_link', 'value': 'Task Link', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def snapshots():
    data_url = '/snapshot/api/snapshots/'
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'short_desc', 'value': 'Description', 'formatter': 'nameFormatter'},
                {'data_field': 'closing_date', 'value': 'Closing Date', 'formatter': 'nameFormatter'},
                {'data_field': 'snapped_at', 'value': 'Snapped At', 'formatter': 'nameFormatter'},
                {'data_field': 'reconciliation', 'value': 'Reconciliation', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def task_audit(task_id):
    data_url = "/audit/api/task_audit/?id=%s" % task_id
    row_defs = [{'data_field': 'timestamp', 'value': 'Time', 'formatter': 'nameFormatter'},
                {'data_field': 'desc', 'value': 'Action', 'formatter': 'nameFormatter'},
                {'data_field': 'comment', 'value': 'Comment', 'formatter': 'nameFormatter'},
                {'data_field': 'user_name', 'value': 'User', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def forecasts():
    data_url = "/forecasts/api/forecasts_list"
    row_defs = [{'data_field': 'id_link', 'value': 'Label', 'formatter': 'nameFormatter'},
                {'data_field': 'start_date', 'value': 'Start Date', 'formatter': 'nameFormatter'},
                {'data_field': 'comment', 'value': 'Comment', 'formatter': 'nameFormatter'}
            ]
    return get_bstrap_table(data_url, row_defs)