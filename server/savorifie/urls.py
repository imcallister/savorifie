from django.conf.urls import include, url
from django.contrib import admin


import main_views

admin.autodiscover()

handler500 = 'main_views.custom_500'

urlpatterns = [
    #url(r'^$', main_views.home, name='home'),
    url(r'^$', main_views.react, name='react'),
    #url(r'^$', main_views.react, name='react'),
    url(r'^api/accounts/', include('accounts.urls')),
    url(r'^maintenance/', main_views.maintenance, name='maintenance'),
    url(r'^reports/$', main_views.reports, name='reports'),
    url(r'^load-orders/$', main_views.load_orders, name='load-orders'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('accounting.urls')),
    url(r'', include('base.urls')),
    url(r'', include('sales.urls')),
    url(r'', include('reports.urls')),
    url(r'', include('inventory.urls')),
    url(r'', include('fulfill.urls')),

    url(r'', include('importers.urls')),

    # general accountifie urls
    url(r'', include('accountifie.urls')),

    url(r'^.*/', main_views.react, name='react')
]
