from django.conf.urls import url
import UPS
import NC2
import FRB
import mcard

urlpatterns = [
    url(r'importers/nc2_upload/$', NC2.upload),
    url(r'importers/upload/ups/$', UPS.upload),
    url(r'importers/upload/frb/$', FRB.upload),
    url(r'importers/upload/mcard/$', mcard.upload),
]
