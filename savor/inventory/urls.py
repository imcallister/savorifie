from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'inventory/sales_history', 'inventory.views.sales_detail'),
    url(r'inventory/output_shopify_no_wrap/$', 'inventory.views.output_shopify_no_wrap'),
    url(r'inventory/reconcile_warehouse/$', 'inventory.views.reconcile_warehouse'),
    url(r'inventory/request_fulfill/(?P<order_id>[_a-zA-Z0-9]+)/$', 'inventory.views.request_fulfill'),
    url(r'^inventory/upload/(?P<file_type>.*)/$', 'inventory.views.upload_file', name='upload_file'),

    url(r'inventory/$', 'inventory.views.main'),
)
