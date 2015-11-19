import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

from models import AuditRecord, Task, TaskDef


def get(api_view, params):
    return globals()[api_view](params)


def get_fld(record, fld):
    if fld == 'user':
        return str(getattr(record, fld))
    elif fld in ['approvers', 'preparers']:
        return ','.join([str(x) for x in getattr(record, fld).all()])
    else:
        return getattr(record, fld)


def get_record_data(record, flds):
    data = dict((fld, get_fld(record, fld)) for fld in flds)
    return data


def get_task_data(task):
        data = {}
        data['id'] = task.id
        data['as_of'] = task.as_of
        data['task_def'] = task.task_def.desc
        data['id_link'] = task.id_link
        data['status_tag'] = task.status_tag
        return data


def tasks(request):
    if request.GET.has_key('date'):
        req_tasks = Task.objects.select_related('task_def').filter(as_of=request.GET['date']).order_by('-as_of')
    else:
        req_tasks = Task.objects.select_related('task_def').all().order_by('-as_of')
    
    def get_task_data(task):
        data = {}
        data['id'] = task.id
        data['as_of'] = task.as_of
        data['task_def'] = task.task_def.desc
        data['id_link'] = task.id_link
        data['status_tag'] = task.status_tag
        return data

    tasks_data = [get_task_data(task) for task in req_tasks]
    tasks_json = json.dumps(tasks_data, cls=DjangoJSONEncoder)
    return HttpResponse(tasks_json, content_type="application/json")


def tasks_list(params):
    tasks = Task.objects.select_related('task_def').all().order_by('-as_of')
    return [get_task_data(task) for task in tasks]


def task_audit(params):
    task_id = params['id']
    records = AuditRecord.objects.filter(task__id=task_id)
    flds = ['timestamp', 'id', 'desc', 'comment', 'user_name']
    return [get_record_data(rec, flds) for rec in records]


def audit_trail(params):
    records = AuditRecord.objects.all()
    flds = ['user', 'timestamp', 'desc', 'comment_fmt','task_link']
    return [get_record_data(rec, flds) for rec in records]


def task_defs(params):
    taskdefs = TaskDef.objects.all()
    flds = ['id', 'freq', 'desc', 'approvers', 'preparers']
    return [get_record_data(taskdef, flds) for taskdef in taskdefs]