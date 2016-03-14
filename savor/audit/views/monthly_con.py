from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext


import audit._helpers as hlp
import tables.bstrap_tables
import accountifie.reporting.api

@login_required
def monthly_signoff(request, id):
    task, user, context, qs, form_type = hlp.prep_task_views(request, id=id)

    context['YR'] = task.as_of.year
    context['MTH'] = "%02d" % task.as_of.month

    request.session['company_id'] = 'SAV'

    context['date'] = task.as_of.strftime('%B %Y')

    context['large_expenses'] = tables.bstrap_tables.large_expenses(task.as_of)
    context['nominal'] = tables.bstrap_tables.nominal(task.as_of)
    context['cap_amort'] = tables.bstrap_tables.balance_trends(task.as_of, acct_list=[str(x) for x in range(1701,1713)])
    context['rev_trends'] = tables.bstrap_tables.balance_trends(task.as_of, accts_path='income')
    context['exp_trends'] = tables.bstrap_tables.balance_trends(task.as_of, accts_path='opexp')

    col_tag = '%dM%s' % (task.as_of.year, '{:02d}'.format(task.as_of.month))
    rpt_context = accountifie.reporting.api.html_report_snippet('ChgInEquityStatement', 'SAV', version='v1', col_tag=col_tag)
    context['cap_rows'] = rpt_context['rows']
    context['cap_col_titles'] = rpt_context['column_titles']


    return render_to_response('audit/monthly_signoff.html', context, context_instance = RequestContext(request))  
