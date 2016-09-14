import os

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from fulfill.models import WarehouseFulfill
import accountifie.toolkit
from accountifie.toolkit.forms import FileForm
import inventory.apiv1 as inventory_api

from .file_models.NC2 import NC2CSVModel
import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')


def order_upload(request):
    form = FileForm(request.POST, request.FILES)

    if form.is_valid():
        upload = request.FILES.values()[0]
        file_name_with_timestamp = accountifie.toolkit.uploader.save_file(upload)
        dupes, new_packs, error_cnt, error_msgs = process_nc2(file_name_with_timestamp)

        messages.success(request, 'Loaded NC2 file: %d new records, \
                                                    %d duplicate records, \
                                                    %d bad rows'
                                   % (new_packs, dupes, error_cnt))
        for e in error_msgs:
            messages.error(request, e)

        context = {}
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        context = {}
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the NC2 file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))


def process_nc2(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    wh_records, errors = NC2CSVModel.import_data(data=open(incoming_name, 'rU'))
    wh_id = inventory_api.warehouse('NC2', {})['id']

    new_recs_ctr = 0
    exist_recs_ctr = 0
    errors_cnt = len(errors)

    for rec in wh_records:
        rec['warehouse_id'] = wh_id
        rec_obj = WarehouseFulfill.objects \
                                  .filter(warehouse_pack_id=rec['warehouse_pack_id']) \
                                  .first()
        if rec_obj:
            # if warehose fulfill object already exists ... skip to next one
            exist_recs_ctr += 1
        else:
            new_recs_ctr += 1
            rec_obj = WarehouseFulfill(**rec)
            rec_obj.save()

    return exist_recs_ctr, new_recs_ctr, errors_cnt, errors