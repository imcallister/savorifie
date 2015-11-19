import json

from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse


from financifie.middleware.docengine import getCurrentUser

import audit.models
from audit.forms import TaskBetterForm
import audit.api
import tables.bstrap_tables


class TaskCreate(CreateView):
    model = audit.models.Task
    form_class = TaskBetterForm
    template_name = 'audit/task_form.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.action = 'create'
        form.instance.user = getCurrentUser()
        return super(TaskCreate, self).form_valid(form)


def api(request, api_view):
    params = request.GET
    return HttpResponse(json.dumps(audit.api.get(api_view, params), cls=DjangoJSONEncoder), content_type="application/json")

@login_required
def tasks(request):
    context = {}
    context['title'] = 'Tasks'
    context['content'] = tables.bstrap_tables.tasks()
    return render_to_response('audit/base_audit.html', context, context_instance=RequestContext(request))



@login_required
def taskdefs(request):
    context = {}
    context['title'] = 'Task Definitions'
    context['content'] = tables.bstrap_tables.task_defs()

    return render_to_response('audit/base_audit.html', context, context_instance=RequestContext(request))

@login_required
def audit_trail(request):
    context = {}
    context['title'] = 'Audit Trail'
    context['content'] = tables.bstrap_tables.audit_trail()
    return render_to_response('audit/base_audit.html', context, context_instance=RequestContext(request))




@login_required
def task_signoff(request):
    if request.method != "POST":
        raise Http404,'Bad request'
    user = request.user
    task_id = request.POST['task_id']
    task = audit.models.Task.objects.get(id=task_id)
    comment = request.POST['comment']
    task.comment = comment
    task.save(action='signoff', user=user, comment=comment)
    url = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(url)
  
@login_required
def task_submit(request):
    if request.method != "POST":
        raise Http404,'Bad request'
    user = request.user
    task_id = request.POST['task_id']
    comment = request.POST['comment']
    task = audit.models.Task.objects.get(id=task_id)
    task.save(action='submit', user=user, comment=comment)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def task_comment(request):
    if request.method != "POST":
        raise Http404,'Bad request'
    user = request.user
    task_id = request.POST['task_id']
    comment = request.POST['comment']
    task = audit.models.Task.objects.get(id=task_id)
    task.save(action='comment', user=user, comment=comment)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
