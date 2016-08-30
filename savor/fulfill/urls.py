from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'fulfill/thoroughbred_upload/$', views.thoroughbred_upload),
    url(r'fulfill/nc2_upload/$', views.nc2_upload),

    url(r'fulfill/reconcile_warehouse/$', views.reconcile_warehouse),

    url(r'fulfill/make_batch/(?P<warehouse>[_a-zA-Z0-9]+)/$', views.make_batch),
    url(r'^fulfill/queue_orders/$', views.queue_orders),

    url(r'^fulfill/batch_list/(?P<batch_id>[_a-zA-Z0-9]+)/$', views.batch_list),    

)
