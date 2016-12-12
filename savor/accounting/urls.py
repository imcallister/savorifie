from django.conf.urls import url
import views
import jobs

urlpatterns = [
    url(r'accounting/assign-COGS$', jobs.assign_FIFO),
    url(r'accounting/$', views.accounting),
]
