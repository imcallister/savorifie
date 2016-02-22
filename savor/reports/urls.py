from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^cash_balances/', 'reports.charts.cash_balances', name='cash_balances'),
    url(r'^expense_trends/', 'reports.charts.expense_trends', name='expense_trends'),

)
