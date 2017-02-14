from django.template import Context
from django.template.loader import get_template

from accountifie.toolkit.utils import get_default_company
from accountifie.toolkit.utils import get_bstrap_table




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

def recent_tasks():
    data_url = "/api/celery/tasks_just_finished"
    row_defs = [{'data_field': 'task_id', 'value': 'Task ID', 'formatter': 'nameFormatter'},
                {'data_field': 'date_done', 'value': 'Time Started', 'formatter': 'nameFormatter'},
                {'data_field': 'task_status', 'value': 'Status', 'formatter': 'nameFormatter'},
                {'data_field': 'task_name', 'value': 'Name', 'formatter': 'nameFormatter'},
                {'data_field': 'result', 'value': 'Result', 'formatter': 'nameFormatter'}
            ]
    return get_bstrap_table(data_url, row_defs)

def UPS_invoices():
    data_url = "/api/fulfill/UPS_invoices"
    row_defs = [{'data_field': 'invoice_number', 'value': 'Invoice #', 'formatter': 'nameFormatter'},
                {'data_field': 'last_date', 'value': 'Sale Date', 'formatter': 'nameFormatter'},
                {'data_field': 'charge', 'value': 'Amount', 'formatter': 'nameFormatter'}
            ]
    return get_bstrap_table(data_url, row_defs)

def IFS_monthly():
    data_url = "/api/fulfill/IFS_monthly"
    row_defs = [{'data_field': 'invoice_number', 'value': 'Invoice #', 'formatter': 'nameFormatter'},
                {'data_field': 'last_date', 'value': 'Sale Date', 'formatter': 'nameFormatter'},
                {'data_field': 'charge', 'value': 'Amount', 'formatter': 'nameFormatter'},
                {'data_field': 'drilldown', 'value': 'Details', 'formatter': 'nameFormatter'}
            ]
    return get_bstrap_table(data_url, row_defs)


def fulfill_no_shipcharge():
    data_url = "/api/fulfill/fulfill_no_shipcharge"
    row_defs = [{'data_field': 'fulfillment_id', 'value': 'Fulfill ID', 'formatter': 'nameFormatter'},
                {'data_field': 'order', 'value': 'Order', 'formatter': 'nameFormatter'},
                {'data_field': 'request_date', 'value': 'Request Date', 'formatter': 'nameFormatter'},
                {'data_field': 'warehouse', 'value': 'Warehouse', 'formatter': 'nameFormatter'},
                {'data_field': 'ship_type', 'value': 'Ship Type', 'formatter': 'nameFormatter'},
                {'data_field': 'bill_to', 'value': 'Billing Acct', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_name', 'value': 'Ship Name', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_company', 'value': 'Ship Company', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def whouse_records(fulfill_id):
    data_url = "api/fulfill/warehousefulfill/?fulfill=%s" % fulfill_id
    row_defs = [{'data_field': 'warehouse_pack_id', 'value': 'Warehouse ID', 'formatter': 'nameFormatter'},
                {'data_field': 'fulfillment', 'value': 'Fulfill ID', 'formatter': 'nameFormatter'},
                {'data_field': 'warehouse', 'value': 'Warehouse', 'formatter': 'nameFormatter'},
                {'data_field': 'request_date', 'value': 'Request Date', 'formatter': 'nameFormatter'},
                {'data_field': 'ship_date', 'value': 'Ship Date', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_type', 'value': 'Ship Type', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_name', 'value': 'Ship Name', 'formatter': 'nameFormatter'},
                {'data_field': 'ship_email', 'value': 'Ship Email', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_cost', 'value': 'Ship Cost', 'formatter': 'nameFormatter'},
                {'data_field': 'handling_cost', 'value': 'Handling', 'formatter': 'nameFormatter'},
                {'data_field': 'tracking_number', 'value': 'Tracking #', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def shipping_info(fulfill_id):
    data_url = "/api/fulfill/shippingcharge/?fulfill=%s" % str(fulfill_id)
    row_defs = [{'data_field': 'tracking_number', 'value': 'Tracking #', 'formatter': 'nameFormatter'},
                {'data_field': 'account', 'value': 'Account', 'formatter': 'nameFormatter'},
                {'data_field': 'invoice_number', 'value': 'Invoice #', 'formatter': 'nameFormatter'},
                {'data_field': 'charge', 'value': 'Charge', 'formatter': 'nameFormatter'},
                {'data_field': 'requested_ship_type', 'value': 'Requested Ship Type', 'formatter': 'nameFormatter'},
                {'data_field': 'warehouse', 'value': 'Warehouse Acct', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def UPS_wrong_acct():
    data_url = "/api/fulfill/UPS_wrong_acct"

    row_defs = [{'data_field': 'tracking_number', 'value': 'Tracking #', 'formatter': 'nameFormatter'},
                {'data_field': 'invoice_number', 'value': 'Invoice #', 'formatter': 'nameFormatter'},
                {'data_field': 'ship_date', 'value': 'Ship Date', 'formatter': 'nameFormatter'},
                {'data_field': 'order_related', 'value': 'Order Related?', 'formatter': 'nameFormatter'},
                {'data_field': 'charge', 'value': 'Amount', 'formatter': 'nameFormatter'},
                {'data_field': 'fulfillment', 'value': 'Fulfillment', 'formatter': 'nameFormatter'},
                {'data_field': 'requested_ship_type', 'value': 'Requested', 'formatter': 'nameFormatter'},
                {'data_field': 'warehouse', 'value': 'Warehouse', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def unpaid_channel(label):
    print '=' * 20

    print 'unpaid channel'
    print '=' * 20
    data_url = "/api/sales/unpaid_channel/%s/" % label
    row_defs = [{'data_field': 'label', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'paid_thru', 'value': 'Paid Via', 'formatter': 'nameFormatter'},
                {'data_field': 'sale_date', 'value': 'Date', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_name', 'value': 'Name', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_company', 'value': 'Company', 'formatter': 'nameFormatter'},
                {'data_field': 'proceeds', 'value': 'Proceeds', 'formatter': 'nameFormatter'},
                {'data_field': 'items_string', 'value': 'SKUs', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def channel_payout_comp(label):
    data_url = "/api/sales/channel_payout_comp/%s/" % label
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'date', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'label', 'value': 'Description', 'formatter': 'nameFormatter'},
                {'data_field': 'payout', 'value': 'Payout', 'formatter': 'nameFormatter'},
                {'data_field': 'calcd_payout', 'value': 'Savor Calc', 'formatter': 'nameFormatter'},
                {'data_field': 'diff', 'value': 'Diff', 'formatter': 'nameFormatter'},
                
            ]
    return get_bstrap_table(data_url, row_defs)

def unit_sales():
    data_url = "/api/sales/unit_sales"
    row_defs = [{'data_field': 'sale_link', 'value': 'Sale ID', 'formatter': 'nameFormatter'},
                {'data_field': 'sale_date', 'value': 'Sale Date', 'formatter': 'nameFormatter'},
                {'data_field': 'sku', 'value': 'SKU', 'formatter': 'nameFormatter'},
                {'data_field': 'fulfill_status', 'value': 'Fulfill status', 'formatter': 'nameFormatter'},
                {'data_field': 'unit_price', 'value': 'Unit Price', 'formatter': 'nameFormatter'},
                {'data_field': 'quantity', 'value': 'Quantity', 'formatter': 'nameFormatter'},
                {'data_field': 'channel', 'value': 'Channel', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def orders_list():
    data_url = "/api/sales/sale/?view=fulfillment"
    row_defs = [{'data_field': 'drilldown', 'value': 'Order ID', 'formatter': 'nameFormatter'},
                {'data_field': 'sale_date', 'value': 'Sale Date', 'formatter': 'nameFormatter'},
                {'data_field': 'channel', 'value': 'Channel', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_name', 'value': 'Name', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_company', 'value': 'Company', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_city', 'value': 'Name', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_zip', 'value': 'Company', 'formatter': 'nameFormatter'},
                {'data_field': 'items_string', 'value': 'SKUs', 'formatter': 'nameFormatter'},
                {'data_field': 'unfulfilled_string', 'value': 'Unfulfilled', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def nominal(dt):
    if type(dt) == str:
        dt_str = dt
    else:
        dt_str = dt.isoformat()

    data_url = "/api/base/nominal/?date=%s" % dt_str
    row_defs = [{'data_field': 'date', 'value': 'Date', 'formatter': 'nameFormatter'},
                {'data_field': 'comment', 'value': 'Comment', 'formatter': 'nameFormatter'},
                {'data_field': 'account0', 'value': 'Account1', 'formatter': 'nameFormatter'},
                {'data_field': 'amount0', 'value': 'Amount1', 'formatter': 'nameFormatter'},
                {'data_field': 'account1', 'value': 'Account2', 'formatter': 'nameFormatter'},
                {'data_field': 'amount1', 'value': 'Amount2', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def nominal_changes(dt):
    data_url = "/api/base/changes/nominal/?date=%s" % dt.isoformat()
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'company_id', 'value': 'Company', 'formatter': 'nameFormatter'},
                {'data_field': 'history_type', 'value': 'Change', 'formatter': 'nameFormatter'},
                {'data_field': 'comment', 'value': 'Comment', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def expense_changes(dt):
    data_url = "/api/base/changes/expense/?date=%s" % dt.isoformat()
    row_defs = [{'data_field': 'id', 'value': 'ID', 'formatter': 'nameFormatter'},
                {'data_field': 'start_date', 'value': 'Start Date', 'formatter': 'nameFormatter'},
                {'data_field': 'glcode', 'value': 'GL Account', 'formatter': 'nameFormatter'},
                {'data_field': 'glcode', 'value': 'GL Account Name', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def tasks():
    data_url = '/audit/api/tasks_list/'
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


def task_audit(task_id):
    data_url = "/audit/api/task_audit/?id=%s" % task_id
    row_defs = [{'data_field': 'timestamp', 'value': 'Time', 'formatter': 'nameFormatter'},
                {'data_field': 'desc', 'value': 'Action', 'formatter': 'nameFormatter'},
                {'data_field': 'comment', 'value': 'Comment', 'formatter': 'nameFormatter'},
                {'data_field': 'user_name', 'value': 'User', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)


def fulfill_requested(warehouse=None):
    if warehouse:
        data_url = "/api/fulfill/requested/?warehouse=%s" % warehouse
    else:
        data_url = "/api/fulfill/requested/"

    row_defs = [
                {'data_field': 'order:external_channel_id', 'value': 'External ID', 'formatter': 'nameFormatter'},
                {'data_field': 'order:id', 'value': 'Sale ID', 'formatter': 'nameFormatter'},
                {'data_field': 'order:shipping_name', 'value': 'Shipping Name', 'formatter': 'nameFormatter'},
                {'data_field': 'order:customer_code', 'value': 'Customer Code', 'formatter': 'nameFormatter'},
                {'data_field': 'order:sale_date', 'value': 'Sale Date', 'formatter': 'nameFormatter'},
                {'data_field': 'order:channel', 'value': 'Channel', 'formatter': 'nameFormatter'},
                {'data_field': 'warehouse', 'value': 'Warehouse', 'formatter': 'nameFormatter'},
                {'data_field': 'items', 'value': 'Items', 'formatter': 'nameFormatter'},
            ]

    return get_bstrap_table(data_url, row_defs)


def no_warehouse_record(warehouse=None):
    if warehouse:
        data_url = "/api/fulfill/no_warehouse_record/?warehouse=%s" % warehouse
    else:
        data_url = "/api/fulfill/no_warehouse_record/"

    row_defs = [
                {'data_field': 'order:external_channel_id', 'value': 'External ID', 'formatter': 'nameFormatter'},
                {'data_field': 'id', 'value': 'Fulfill ID', 'formatter': 'nameFormatter'},
                {'data_field': 'order:shipping_name', 'value': 'Shipping Name', 'formatter': 'nameFormatter'},
                {'data_field': 'order:customer_code', 'value': 'Customer Code', 'formatter': 'nameFormatter'},
                {'data_field': 'order:sale_date', 'value': 'Sale Date', 'formatter': 'nameFormatter'},
                {'data_field': 'order:channel', 'value': 'Channel', 'formatter': 'nameFormatter'},
                {'data_field': 'warehouse', 'value': 'Warehouse', 'formatter': 'nameFormatter'},
                {'data_field': 'items', 'value': 'Items', 'formatter': 'nameFormatter'},
            ]

    return get_bstrap_table(data_url, row_defs)

def fulfill_confirmed():
    data_url = "/api/fulfill/fulfilled/"
    row_defs = [{'data_field': 'id', 'value': 'Request ID', 'formatter': 'nameFormatter'},
                {'data_field': 'shipping_name', 'value': 'Shipping Name', 'formatter': 'nameFormatter'},
                {'data_field': 'customer_code', 'value': 'Customer Code', 'formatter': 'nameFormatter'},
                {'data_field': 'sale_date', 'value': 'Sale Date', 'formatter': 'nameFormatter'},
                {'data_field': 'channel', 'value': 'Channel', 'formatter': 'nameFormatter'},
                {'data_field': 'external_channel_id', 'value': 'External ID', 'formatter': 'nameFormatter'},
                {'data_field': 'gift_wrapping', 'value': 'Gift Wrapping', 'formatter': 'nameFormatter'},
                {'data_field': 'items_string', 'value': 'Items', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def unfulfilled():
    data_url = "/api/fulfill/unfulfilled/"
    row_defs = [{'data_field': 'shipping_name', 'value': 'Name', 'formatter': 'nameFormatter'},
                {'data_field': 'customer_code', 'value': 'Customer', 'formatter': 'nameFormatter'},
                {'data_field': 'items_string', 'value': 'Items', 'formatter': 'nameFormatter'},
                {'data_field': 'external_channel_id', 'value': 'external_id', 'formatter': 'nameFormatter'},
                {'data_field': 'gift_wrapping', 'value': 'Gift Wrapping', 'formatter': 'nameFormatter'},
                {'data_field': 'gift_message', 'value': 'Gift Message', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)

def thoroughbred_mismatch():
    data_url = "/api/inventory/thoroughbred_mismatch/"
    row_defs = [{'data_field': 'savor', 'value': 'Savor Details', 'formatter': 'nameFormatter'},
                {'data_field': 'thoroughbred', 'value': 'Thoroughbred Details', 'formatter': 'nameFormatter'},
                {'data_field': 'mismatch', 'value': 'Mismatch?', 'formatter': 'nameFormatter'},
            ]
    return get_bstrap_table(data_url, row_defs)
