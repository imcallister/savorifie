from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    
    url(r'^orders_list$', 'inventory.views.orders'),
    url(r'^order/drilldown/(?P<order_id>[_a-zA-Z0-9]+)/$', 'inventory.views.order_drilldown'),
    
)
