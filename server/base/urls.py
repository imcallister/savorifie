from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^download_expenses/$', views.output_expenses),
    url(r'^long_calc2/$', views.long_calc2),
    url(r'^long_calc_task/$', views.long_calc_task),
    #url(r'^long_calc_tri_11/$', views.tri_11),
 ]
