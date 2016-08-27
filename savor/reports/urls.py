from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^cash_balances/', 'reports.charts.cash_balances', name='cash_balances'),
    url(r'^expense_trends/', 'reports.charts.expense_trends', name='expense_trends'),

    url(r'^inventory/management/$', views.management),
    url(r'^inventory/$', views.main),
    
)
