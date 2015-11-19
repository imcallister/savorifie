import models
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin



class TaskDefAdmin(SimpleHistoryAdmin):
    filter_horizontal = ('preparers','approvers',)
    list_display=('freq', 'tmpl',)

class TaskAdmin(SimpleHistoryAdmin):
    list_display=('status', 'task_def', 'as_of',)


admin.site.register(models.TaskDef, TaskDefAdmin)
admin.site.register(models.Task, TaskAdmin)