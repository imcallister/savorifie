from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'inventory/sales_history', 'inventory.views.sales_detail'),
    url(r'inventory/output_shopify_no_wrap/$', 'inventory.views.output_shopify_no_wrap'),
    url(r'inventory$', 'inventory.views.main'),
    
)
