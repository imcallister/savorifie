from django.conf.urls import url

import views
import reports.charts

urlpatterns = [
    url(r'^cash_balances/', reports.charts.cash_balances, name='cash_balances'),
    url(r'^expense_trends/', reports.charts.expense_trends, name='expense_trends'),

    url(r'^order/drilldown/(?P<order_id>[_a-zA-Z0-9]+)/$', views.order_drilldown),
    url(r'^orders_list/$', views.orders),
    url(r'^sales-analysis/$', views.sales_analysis, name='sales_analysis'),

    url(r'^inventory/management/$', views.management),
    url(r'^inventory/$', views.inventory_counts),
    url(r'^ship_charges/$', views.ship_charges),
    url(r'^bookkeeping/', views.bookkeeping, name='bookkeeping'),
    url(r'^receivables/', views.receivables, name='receivables'),
    url(r'^shippingcosts/', views.shippingcosts, name='shippingcosts'),
]
