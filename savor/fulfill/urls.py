from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
import views

urlpatterns = patterns('',
    url(r'inventory/thoroughbred_upload/$', view.thoroughbred_upload),
    url(r'inventory/nc2_upload/$', views.nc2_upload),
    url(r'^inventory/upload/(?P<file_type>.*)/$', views.upload_file, name='upload_file'),

    url(r'inventory/reconcile_warehouse/$', views.reconcile_warehouse),
    url(r'inventory/request_fulfill/(?P<warehouse>[_a-zA-Z0-9]+)/(?P<order_id>[_a-zA-Z0-9]+)/$', views.request_fulfill),
    
    url(r'inventory/make_batch/(?P<warehouse>[_a-zA-Z0-9]+)/$', views.make_batch),
    url(r'^inventory/queue_orders/$', views.queue_orders),

)

urlpatterns += format_suffix_patterns([
    url(r'^fulfillment/$', views.FulfillmentList.as_view()),
    url(r'^fulfillment/(?P<pk>[0-9]+)/$', views.FulfillmentDetail.as_view()),
])

