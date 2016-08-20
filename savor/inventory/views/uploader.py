from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from accountifie.toolkit.forms import FileForm
import accountifie.toolkit
import inventory.importers


@login_required
def thoroughbred_upload(request):
    return inventory.importers.thoroughbred.order_upload(request)

@login_required
def nc2_upload(request):
    return inventory.importers.nc2.order_upload(request)


@login_required
def upload_file(request, file_type, check=False):

    if request.method == 'POST':
        if file_type == 'thoroughbred':
            return inventory.importers.thoroughbred.order_upload(request)
        elif file_type == 'nc2':
            return inventory.importers.nc2.order_upload(request)
        else:
            raise ValueError("Unexpected file type; know about thoroughbred")

        return accountifie.toolkit.uploader.upload_file(request, **config)
    else:
        form = FileForm()
        context = {'form': form, 'file_type': file_type}
        return render_to_response('base/upload_csv.html', context,
                                  context_instance=RequestContext(request))
