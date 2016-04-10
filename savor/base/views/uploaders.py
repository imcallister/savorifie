
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponseRedirect

import base.importers
from base.models import Cashflow, make_expense_stubs
from accountifie.toolkit.forms import FileForm
import accountifie.toolkit

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
def bulk_expense_stubs(request):
    if request.method == 'POST':
        cps = [x[7:] for x in request.POST if x[:7]=='create_']
        qs = list(Cashflow.objects.filter(counterparty_id__in=cps).values())
        rslts = make_expense_stubs(qs)

        messages.info(request, "%d new stub expenses created. %d duplicates found and not created" % (rslts['new'], rslts['duplicates']))
        return HttpResponseRedirect("/admin/base/expense/?unmatched=UNMATCHED")
    else:
        raise ValueError("This resource requires a POST request")
