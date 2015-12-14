from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView, TemplateView
from django.core.urlresolvers import reverse_lazy


import main_views

admin.autodiscover()


urlpatterns = patterns('',

    # main front pages
    url(r'^$', main_views.home, name='home'),
    url(r'^maintenance/', main_views.maintenance, name='maintenance'),
    url(r'^daily/', main_views.daily, name='daily'),
    url(r'^reports/$', main_views.reports, name='reports'),

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'', include('base.urls')),
    url(r'', include('accountifie.toolkit.urls')),
    url(r'', include('accountifie.common.urls')),

    url(r'^forecasts/', include('accountifie.forecasts.urls')),
    url(r'^gl/', include('accountifie.gl.urls')),
    url(r'^snapshot/', include('accountifie.snapshot.urls')),
    url(r'^reporting/', include('accountifie.reporting.urls')),
    url(r'^environment/', include('accountifie.environment.urls')),
    url(r'^audit/', include('audit.urls')),    
    
    
)
