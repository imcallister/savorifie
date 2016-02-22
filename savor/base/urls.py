from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
 
    
    url(r'^download_expenses/$', views.output_expenses),

    url(r'^dump_fixtures/$', views.dump_fixtures),
    
    url(r'^base/upload/(?P<file_type>.*)/$', views.upload_file, name='upload_file'),    
    
    
)
