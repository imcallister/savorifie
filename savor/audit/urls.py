from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
 
    url(r'audit/^$', views.tasks, name='audit_index'),
    url(r'audit/tasks/$', views.tasks, name='tasks'),

    #url(r'api/(?P<api_view>[_a-zA-Z0-9]+)/$', views.api),

    url(r'audit/audit_trail/$', views.audit_trail, name='audit_trail'),
    url(r'audit/task/add/$', views.TaskCreate.as_view(), name="task_form"),
    url(r'audit/task/submit/$', views.task_submit, name="task_submit"),
    url(r'audit/task/signoff/$', views.task_signoff, name="task_signoff"),
    url(r'audit/task/comment/$', views.task_comment, name="task_comment"),

    url(r'audit/task/daily_expenses/(?P<id>[()_a-zA-Z0-9]+)/$', views.daily_expenses),
    url(r'audit/records/$', views.audit_trail, name='audit_trail'),
    url(r'audit/taskdefs/$', views.taskdefs, name='taskdefs'),
    url(r'audit/task/monthly_signoff/(?P<id>[()_a-zA-Z0-9]+)/$', views.monthly_signoff, name='monthly_signoff'),
    
)
