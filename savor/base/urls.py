from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
 
    
    url(r'^download_expenses/$', views.output_expenses),
    
    url(r'^base/upload/(?P<file_type>.*)/$', views.upload_file, name='upload_file'),    
    
    url(r'^chart_data_json/', 'reports.charts.chart_data_json', name='chart_data_json'),
    url(r'^chart_data_json2/', 'reports.charts.chart_data_json2', name='chart_data_json2'),
    url(r'^chart_data_json3/', 'reports.charts.chart_data_json3', name='chart_data_json3'),
    url(r'^chart_data_json4/', 'reports.charts.chart_data_json4', name='chart_data_json4'),


    
)
