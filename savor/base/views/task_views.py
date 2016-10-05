from __future__ import absolute_import

from time import sleep

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import JsonResponse

from accountifie.celery import background_task
#from accountifie.celery.celery_main import app as celery_app


"""
from celery import shared_task


@shared_task
def tri_11(request):
    tot = 0
    for i in range(10):
        sleep(1)
        tot += i
    return tot
"""

# long-running calc
def tri_10():
    tot = 0
    for i in range(10):
        sleep(1)
        tot += i
    return tot


def long_calc2(request):
    return render_to_response('long_task2.html',
                              RequestContext(request, {}))


def long_calc_task(request):
    
    task_name = 'long_calc2'
    task_id = background_task(task=task_name, calc=tri_10).id
    status_url = 'background_task/status/%s' % task_id
    return JsonResponse({'task_id': task_id, 'task_name': task_name, 'status_url': status_url})
