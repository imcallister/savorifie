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
    
    url(r'', include('audit.urls')),
    url(r'', include('base.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^inventory/', include('inventory.urls')),

    # general accountifie urls
    url (r'', include('accountifie.urls'))
    
)
