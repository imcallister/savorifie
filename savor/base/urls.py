from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',

    url(r'^download_expenses/$', views.output_expenses),
    url(r'^download_salestax/$', views.output_salestax),
    url(r'^download_allsales/$', views.allsales_dump),
    url(r'^download_grosses/$', views.output_grosses),
    url(r'^assign_COGS/$', views.assign_COGS),
    url(r'^base/shopify_upload/$', views.shopify_upload),
    url(r'^base/upload/(?P<file_type>.*)/$', views.upload_file, name='upload_file'),
    url(r'^base/management/$', 'base.views.management'),
    url(r'^base/bulk_expense_stubs/$', views.bulk_expense_stubs),
)
