from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accountifie.common.table import get_table
from accountifie.toolkit.forms import FileForm


@login_required
def ship_charges(request):
    context = {'upload_form': FileForm()}
    context['UPS_invoices'] = get_table('UPS_invoices')
    context['IFS_monthly'] = get_table('IFS_monthly')

    return render(request, 'reports/ship_charges.html', context)
