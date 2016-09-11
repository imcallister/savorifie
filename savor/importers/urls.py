from django.conf.urls import patterns, include, url
import NC2

urlpatterns = patterns('',
    url(r'importers/nc2_upload/$', NC2.order_upload),

)
