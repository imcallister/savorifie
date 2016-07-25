from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import model_views

urlpatterns = patterns('',
    url(r'inventory/sales_history', 'inventory.views.sales_detail'),
    #url(r'inventory/output_shopify_no_wrap/$', 'inventory.views.output_shopify_no_wrap'),
    url(r'inventory/reconcile_warehouse/$', 'inventory.views.reconcile_warehouse'),
    url(r'inventory/request_fulfill/(?P<warehouse>[_a-zA-Z0-9]+)/(?P<order_id>[_a-zA-Z0-9]+)/$', 'inventory.views.request_fulfill'),
    url(r'inventory/thoroughbred_upload/$', 'inventory.views.thoroughbred_upload'),
    url(r'inventory/thoroughbred_list/(?P<batch_id>[_a-zA-Z0-9]+)/$', 'inventory.views.thoroughbred_list'),

    url(r'inventory/make_batch/(?P<warehouse>[_a-zA-Z0-9]+)/$', 'inventory.views.make_batch'),
    url(r'^inventory/upload/(?P<file_type>.*)/$', 'inventory.views.upload_file', name='upload_file'),

    url(r'^inventory/management/$', 'inventory.views.management'),
    url(r'^inventory/$', 'inventory.views.main'),
)


urlpatterns += format_suffix_patterns([
    url(r'^warehouse/$', model_views.WarehouseList.as_view()),
    url(r'^warehouse/(?P<pk>[0-9]+)/$', model_views.WarehouseDetail.as_view()),

    url(r'^fulfillment/$', model_views.FulfillmentList.as_view()),
    url(r'^fulfillment/(?P<pk>[0-9]+)/$', model_views.FulfillmentDetail.as_view()),
])
