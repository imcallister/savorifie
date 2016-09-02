from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView, TemplateView
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from django.conf.urls import handler500

from graphene.contrib.django.views import GraphQLView

import main_views

admin.autodiscover()

handler500 = 'main_views.custom_500'

urlpatterns = patterns('',

    # main front pages
    
    url(r'^$', main_views.home, name='home'),
    url(r'^maintenance/', main_views.maintenance, name='maintenance'),
    url(r'^reports/$', main_views.reports, name='reports'),
    
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')) ,
    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('audit.urls')),
    url(r'', include('base.urls')),
    url(r'', include('sales.urls')),
    url(r'', include('reports.urls')),
    url(r'', include('inventory.urls')),
    url(r'', include('fulfill.urls')),

    # general accountifie urls
    url (r'', include('accountifie.urls'))
)
