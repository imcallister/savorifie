import os, csv, json
from ast import literal_eval
from StringIO import StringIO
import datetime
import gzip
import csv
import datetime
from dateutil.parser import parse

import logging
import pandas as pd

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from forms import FileForm

from accountifie.tasks.utils import task, utcnow
from accountifie.tasks.models import DeferredTask, isDetachedTask, setProgress, setStatus


from accountifie.gl.models import ExternalBalance, Transaction, TranLine

from accountifie.query.query_manager import QueryManager
import base.models as base
from accountifie.forecasts.models import Forecast
from accountifie.gl.models import Company
import accountifie.gl.api
import accountifie.environment.api
import accountifie.toolkit
import base.api
from .models import Expense, Mcard, NominalTransaction, NominalTranLine
import base.importers

import accountifie._utils


logger = logging.getLogger('default')

def api(request, api_view):
    params = request.GET
    return HttpResponse(json.dumps(base.api.get(api_view, params), cls=DjangoJSONEncoder), content_type="application/json")



# TODO   MOVE TO API

@login_required
def large_expenses(request):
    dt = parse(request.GET.get('date'))
    return HttpResponse(json.dumps(base.api.large_expenses(dt), cls=DjangoJSONEncoder), content_type="application/json")


@login_required
def dump_fixtures(request):
    output = StringIO()

    call_command('dumpdata', 'auth.group', 'auth.user', 'gl.company', 'gl.department', 'gl.employee', 'gl.counterparty',
                  'gl.account', 'gl.externalaccount', 'environment', 'audit', 'reporting', 'base','--indent=2', stdout=output)
    data = output.getvalue()
    output.close()

    file_label = 'fixtures_%s' % datetime.datetime.now().strftime('%d-%b-%Y_%H-%M')
    response = HttpResponse(data, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=%s' % file_label
    return response





@login_required
def nominal(request):
    dt = parse(request.GET.get('date'))
    return HttpResponse(json.dumps(base.api.nominal(dt), cls=DjangoJSONEncoder), content_type="application/json")


def company_context(request):
    """Context processor referenced in settings.
    This puts the current company ID into any request context, 
    thus allowing templates to refer to it

    This is not a view.
    """
    company_id = accountifie._utils.get_company(request)
    data = {'company_id': company_id, 'logo': settings.LOGO, 'site_title': settings.SITE_TITLE}
    data['admin_site_title'] = settings.SITE_TITLE
    data['ap_acct'] = accountifie.environment.api.variable({'name':'GL_ACCOUNTS_PAYABLE'})
    
    if company_id:
        try:
            company = Company.objects.get(pk=company_id)
            data.update({'company':company})
            data.update({'color_code': company.color_code})
        except Company.DoesNotExist:
            pass 
    return data




@login_required
def model_changes(request, model_type):
    dt = parse(request.GET.get('date')).date()

    if model_type == 'expense':
        return HttpResponse(base.expense.get_changed(dt), content_type="application/json")
    elif model_type == 'nominal':
        return HttpResponse(base.nominal.get_changed(dt), content_type="application/json")
    else:
        return


@login_required
def choose_company(request, company_id):
    "Hit this to switch companies"

    company_list = [x.id for x in Company.objects.all()]
    
    if company_id not in company_list:
        raise ValueError('%s is not a valid company' % company_id)
    request.session['company_id'] = company_id
    dest =  request.META.get('HTTP_REFERER', '/')
    return HttpResponseRedirect(dest)



@login_required
def upload_file(request, file_type, check=False):

    if request.method == 'POST':
        if file_type == 'expense':
            config = dict(file_type=file_type,
                          model='base.Expense', 
                          unique=base.importers.unique_expense, 
                          name_cleaner=base.importers.clean_expense_fields, 
                          value_cleaner=base.importers.clean_expense_values,
                          exclude=base.importers.exclude_expense(),
                          post_process=None)
        elif file_type == 'frbchecking':
            config = dict(file_type=file_type,
                          model='base.Cashflow', 
                          unique=base.importers.unique_frbchecking, 
                          name_cleaner=base.importers.clean_frbchecking_fields, 
                          value_cleaner=base.importers.clean_frbchecking_values,
                          exclude=[],
                          post_process=None)
        elif file_type == 'shopify':
          return base.importers.shopify.order_upload(request)
        else:
            raise ValueError("Unexpected file type; know about expense, checking, saving, mcard")

        return accountifie.toolkit.uploader.upload_file(request, **config)
    else:
        form = FileForm()
        context = {'form': form, 'file_type': file_type}
        return render_to_response('base/upload_csv.html', context,
                              context_instance=RequestContext(request))
    




@login_required
def output_expenses(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)

    all_expenses = base.Expense.objects.all()
    
    header_row = [unicode(x).encode('utf-8') for x in all_expenses[0].__dict__.keys()]

    writer.writerow(header_row)
    for ex in all_expenses:
        line = [unicode(x).encode('utf-8') for x in ex.__dict__.values()]
        writer.writerow(line)
    return response