from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def shippingcosts(request):
    return render(request, 'reports/shippingcosts.html', {})
