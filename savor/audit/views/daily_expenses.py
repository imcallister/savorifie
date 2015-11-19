from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext


import audit._helpers as hlp
import tables.bstrap_tables


@login_required
def daily_expenses(request, id=None):
    task, user, context, qs, form_type = hlp.prep_task_views(request, id=id)
    
    context['date'] = task.as_of.isoformat()

    context['check_bals'] = tables.bstrap_tables.check_external_bals(task.as_of)
    context['nominal_changes'] = tables.bstrap_tables.nominal_changes(task.as_of)
    context['expense_changes'] = tables.bstrap_tables.expense_changes(task.as_of)
    
    return render_to_response('audit/daily_expenses.html', context,  context_instance = RequestContext(request))