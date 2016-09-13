from django.conf.urls import patterns, include, url
import UPS
import NC2

urlpatterns = patterns('',
    url(r'importers/nc2_upload/$', NC2.order_upload),
    url(r'importers/ups_upload/$', UPS.order_upload),
)
