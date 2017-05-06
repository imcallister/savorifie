from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def sales_analysis(request):
    context = {}
    return render(request, 'reports/sales_analysis.html',context)
