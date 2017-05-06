from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def accounting(request):
    return render(request, 'accounting/main.html', {})

