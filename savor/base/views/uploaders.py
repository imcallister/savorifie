
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponseRedirect

from base.models import Cashflow, CreditCardTrans, make_expense_stubs, make_stubs_from_ccard
from accountifie.toolkit.forms import FileForm
import accountifie.toolkit
import base.importers


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
        elif file_type == 'frbchecking_old':
            config = dict(file_type=file_type,
                          model='base.Cashflow', 
                          unique=base.importers.unique_frbchecking, 
                          name_cleaner=base.importers.clean_frbchecking_fields, 
                          value_cleaner=base.importers.clean_frbchecking_values,
                          exclude=[],
                          post_process=None)
        elif file_type == 'frbchecking':
            return base.importers.frbchecking.order_upload(request)
        elif file_type == 'shopify':
            return base.importers.shopify.order_upload(request)
        elif file_type == 'mastercard':
            return base.importers.creditcard.ccard_upload(request)
        else:
            raise ValueError("Unexpected file type; know about expense, checking, saving, mcard")

        return accountifie.toolkit.uploader.upload_file(request, **config)
    else:
        form = FileForm()
        context = {'form': form, 'file_type': file_type}
        return render(request, 'base/upload_csv.html', context)


@login_required
def bulk_expense_stubs(request):
    if request.method == 'POST':
        cps = [x[7:] for x in request.POST if x[:7]=='create_']
        cf_qs = list(Cashflow.objects.filter(counterparty_id__in=cps).values())
        cf_rslts = make_expense_stubs(cf_qs)

        cc_qs = list(CreditCardTrans.objects.filter(counterparty_id__in=cps).values())
        cc_rslts = make_stubs_from_ccard(cc_qs)

        messages.info(request, "%d new stub expenses created. \
                                %d duplicates found and not created"
                               % (cf_rslts['new'] + cc_rslts['new'],
                                  cf_rslts['duplicates'] + cc_rslts['duplicates']))

        return HttpResponseRedirect("/admin/base/expense/?unmatched=UNMATCHED")
    else:
        raise ValueError("This resource requires a POST request")
