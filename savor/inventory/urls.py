from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'sales_history', 'inventory.views.sales_detail'),
    url(r'$', 'inventory.views.main'),
    

)
