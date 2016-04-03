from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
 
    url(r'^download_expenses/$', views.output_expenses),
    url(r'api/base/(?P<resource>[_a-zA-Z0-9]+)/(?P<item>(.+))/$', 'savor.base.views.get_item'),
    url(r'api/base/(?P<resource>[_a-zA-Z0-9]+)/$', 'savor.base.views.get_resource'),

    
    url(r'^base/upload/(?P<file_type>.*)/$', views.upload_file, name='upload_file'),    
    
    
)
