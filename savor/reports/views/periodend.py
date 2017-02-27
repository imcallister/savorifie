import datetime
from dateutil.parser import parse

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accountifie.toolkit.forms import FileForm


@login_required
def periodend(request):
    context = {'upload_form': FileForm()}
    if request.GET.get('as_of'):
        context['as_of'] = parse(request.GET.get('as_of')).date()   
    else:
        context['as_of'] = datetime.datetime.now().date()
    return render(request, 'reports/periodend.html', context)
