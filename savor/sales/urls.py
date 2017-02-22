from django.conf.urls import url
import views

urlpatterns = [
    url(r'^download_salestax/$', views.output_salestax),
    url(r'^download_allsales/$', views.allsales_dump),
    url(r'^download_grosses/$', views.output_grosses),
    url(r'^sales/shopify_upload/$', views.shopify_upload),
    url(r'^sales/buybuy_upload/$', views.buybuy_upload),
    url(r'^assign_COGS/$', views.assign_COGS),
]
