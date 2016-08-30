from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^cash_balances/', 'reports.charts.cash_balances', name='cash_balances'),
    url(r'^expense_trends/', 'reports.charts.expense_trends', name='expense_trends'),

    url(r'^order/drilldown/(?P<order_id>[_a-zA-Z0-9]+)/$', views.order_drilldown),
    url(r'^orders_list$', views.orders),
    url(r'^inventory/management/$', views.management),
    url(r'^inventory/$', views.inventory_counts),
    

)
