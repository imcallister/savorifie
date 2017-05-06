from django.contrib.auth.decorators import login_required

import fulfill.importers


@login_required
def thoroughbred_upload(request):
    return fulfill.importers.thoroughbred.order_upload(request)


@login_required
def nc2_upload(request):
    return fulfill.importers.nc2.order_upload(request)
