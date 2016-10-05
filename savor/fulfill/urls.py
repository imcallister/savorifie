from django.conf.urls import url
import views

urlpatterns = [
    url(r'fulfill/thoroughbred_upload/$', views.thoroughbred_upload),
    url(r'fulfill/reconcile_warehouse/$', views.reconcile_warehouse),
    url(r'fulfill/shipping/$', views.shipping),
    url(r'fulfill/make_batch/(?P<warehouse>[_a-zA-Z0-9]+)/$', views.make_batch),
    url(r'^fulfill/queue_orders/$', views.queue_orders),
    url(r'^fulfill/batch_list/(?P<batch_id>[_a-zA-Z0-9]+)/$', views.batch_list),    
]
