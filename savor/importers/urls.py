from django.conf.urls import url
import UPS
import NC2
import Franklin
import FRB
import mcard
import IFS_monthly


urlpatterns = [
    url(r'importers/nc2_upload/$', NC2.upload),
    url(r'importers/frank_upload/$', Franklin.upload),
    url(r'importers/upload/ups/$', UPS.upload),
    url(r'importers/upload/frb/$', FRB.upload),
    url(r'importers/upload/mcard/$', mcard.upload),
    url(r'importers/upload/IFSmonthly/$', IFS_monthly.upload),
]
