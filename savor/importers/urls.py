from django.conf.urls import url
import UPS
import NC2

urlpatterns = [
    url(r'importers/nc2_upload/$', NC2.order_upload),
    url(r'importers/ups_upload/$', UPS.order_upload)
]
