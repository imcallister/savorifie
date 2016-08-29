from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^download_salestax/$', views.output_salestax),
    url(r'^download_allsales/$', views.allsales_dump),
    url(r'^download_grosses/$', views.output_grosses),
    url(r'^base/shopify_upload/$', views.shopify_upload),
    url(r'^assign_COGS/$', views.assign_COGS),
    
)
