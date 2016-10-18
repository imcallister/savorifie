from django.conf.urls import url
import UPS
import NC2
import FRB

urlpatterns = [
    url(r'importers/nc2_upload/$', NC2.upload),
    url(r'importers/ups_upload/$', UPS.order_upload),
    url(r'importers/upload/frb/$', FRB.upload),
]
