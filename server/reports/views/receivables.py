from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def receivables(request):
    return render(request, 'reports/receivables.html', {})
