from __future__ import absolute_import

from time import sleep
import datetime

from django.shortcuts import render
from django.template import RequestContext
from django.http import JsonResponse

from accountifie.celery import background_task

# long-running calc
def tri_10(*args, **kwargs):
    tot = 0
    for i in range(20):
        sleep(1)
        tot += i
    return {'return_value': tot}


def long_calc2(request):
    return render(request, 'long_task2.html', {})


def long_calc_task(request):
    task_name = 'long_calc2'
    task_id = background_task(task=task_name, calc=tri_10).id
    status_url = 'background_task/status/%s' % task_id
    return JsonResponse({'task_id': task_id, 'task_name': task_name, 'status_url': status_url})
