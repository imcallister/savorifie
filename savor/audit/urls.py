from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
 
    url(r'^$', views.tasks, name='audit_index'),
    url(r'tasks/$', views.tasks, name='tasks'),

    url(r'api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),

    url(r'audit_trail/$', views.audit_trail, name='audit_trail'),
    url(r'task/add/$', views.TaskCreate.as_view(), name="task_form"),
    url(r'task/submit/$', views.task_submit, name="task_submit"),
    url(r'task/signoff/$', views.task_signoff, name="task_signoff"),
    url(r'task/comment/$', views.task_comment, name="task_comment"),

    url(r'task/daily_expenses/(?P<id>[()_a-zA-Z0-9]+)/$', views.daily_expenses),
    url(r'^records/$', views.audit_trail, name='audit_trail'),
    url(r'^taskdefs/$', views.taskdefs, name='taskdefs'),

    url(r'^task/monthly_signoff/(?P<id>[()_a-zA-Z0-9]+)/$', views.monthly_signoff, name='monthly_signoff'),
    
)
