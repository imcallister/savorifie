from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',

    url(r'^download_expenses/$', views.output_expenses),
    url(r'^base/upload/(?P<file_type>.*)/$', views.upload_file, name='upload_file'),
    url(r'^base/management/$', 'base.views.management'),
    url(r'^base/bulk_expense_stubs/$', views.bulk_expense_stubs),
)
