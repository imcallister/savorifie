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

from financifie.toolkit.forms import FileForm, SplashForm

from financifie.tasks.utils import task, utcnow
from financifie.tasks.models import DeferredTask, isDetachedTask, setProgress, setStatus


from financifie.gl.models import ExternalBalance, Transaction, TranLine

from financifie.query.query_manager import QueryManager
import base.models as base
from financifie.forecasts.models import Forecast
from financifie.gl.models import Company
import financifie.gl.api
import financifie.environment.api
import financifie.toolkit
import base.api
from .models import Expense, Mcard, NominalTransaction, NominalTranLine
import base.importers

import base_settings
import financifie._utils


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
def nominal(request):
    dt = parse(request.GET.get('date'))
    return HttpResponse(json.dumps(base.api.nominal(dt), cls=DjangoJSONEncoder), content_type="application/json")


def company_context(request):
    """Context processor referenced in settings.
    This puts the current company ID into any request context, 
    thus allowing templates to refer to it

    This is not a view.
    """
    
    company_id = financifie._utils.get_company(request)
    data = {'company_id': company_id}
    if company_id:
        try:
            company = Company.objects.get(pk=company_id)
            data.update({'company':company})
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
        elif file_type == 'jpmchecking':
            config = dict(file_type=file_type,
                          model='base.Cashflow', 
                          unique=base.importers.unique_jpmchecking, 
                          name_cleaner=base.importers.clean_jpmchecking_fields, 
                          value_cleaner=base.importers.clean_jpmchecking_values,
                          exclude=[],
                          post_process=None)
        elif file_type == 'jpmsaving':
            config = dict(file_type=file_type,
                          model='base.Cashflow', 
                          unique=base.importers.unique_jpmsaving, 
                          name_cleaner=base.importers.clean_jpmsaving_fields, 
                          value_cleaner=base.importers.clean_jpmsaving_values,
                          exclude=[],
                          post_process=None)
        elif file_type == 'frbchecking':
            config = dict(file_type=file_type,
                          model='base.Cashflow', 
                          unique=base.importers.unique_frbchecking, 
                          name_cleaner=base.importers.clean_frbchecking_fields, 
                          value_cleaner=base.importers.clean_frbchecking_values,
                          exclude=[],
                          post_process=None)
        elif file_type == 'mcard':
            config = dict(file_type=file_type,
                          model='base.Mcard', 
                          unique=base.importers.unique_mcard, 
                          name_cleaner=base.importers.clean_jpmchecking_fields, 
                          value_cleaner=base.importers.clean_jpmchecking_values,
                          exclude=[],
                          post_process=None)
        else:
            raise ValueError("Unexpected file type; know about expense, checking, saving, mcard")

        return financifie.toolkit.uploader.upload_file(request, **config)
    else:
        form = FileForm()
        context = {'form': form, 'file_type': file_type}
        return render_to_response('base/upload_csv.html', context,
                              context_instance=RequestContext(request))
    
def expense_drilldown(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="drilldown.csv"'
    writer = csv.writer(response)

    drilldown = calc_drilldown()

    writer.writerow(list(drilldown.index.names) + list(drilldown.columns))
    for row_idx in drilldown.index:
        line = list(drilldown.loc[row_idx].name) + list(drilldown.loc[row_idx].values)
        writer.writerow(line)
    return response


def calc_drilldown():
    accts = financifie.gl.api.accounts({})
    ACCT_MAP = dict((acct['id'], acct['display_name']) for acct in accts)

    acct_list = [str(x) for x in range(7000,7100)]
    acct_list += ['1705','1250']
    history = QueryManager().pd_history('SAV', 'account_list', None, incl=acct_list, excl_contra=['4150'])

    drop = ['4150','3005','1103']

    
    history = history[~history['contra_accts'].isin(drop)]
    history['month'] = history['date'].map(lambda x: datetime.date(x.year, x.month, 1))
    history['name'] = history['account_id'].map(lambda x: ACCT_MAP[x] if x in ACCT_MAP else None)
    drilldown = history[['month','account_id','name','counterparty','amount']].groupby(['month','name','account_id','counterparty']).sum().unstack(level='month')
    drilldown.columns = drilldown.columns.droplevel()
    drilldown.fillna(0,inplace=True)

    top_cps = ['GOOG']

    drilldown.index = pd.MultiIndex.from_tuples(drilldown.index.map(lambda x: (x[0], x[1], x[2] if x[2] in top_cps else '(various)')), names=['name','acct','cp'])
    drilldown = drilldown.groupby(level=['name','acct','cp']).sum().dropna()
    drilldown['Total'] = drilldown.sum(axis=1)

    drilldown.sortlevel(level='acct', inplace=True)
    return drilldown


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