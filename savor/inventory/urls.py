from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'inventory/sales_history', 'inventory.views.sales_detail'),
    url(r'inventory/output_shopify_no_wrap/$', 'inventory.views.output_shopify_no_wrap'),
    url(r'inventory/request_fulfill/(?P<order_id>[_a-zA-Z0-9]+)/$', 'inventory.views.request_fulfill'),
    
    url(r'inventory/$', 'inventory.views.main'),
    
)
