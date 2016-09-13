import os

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from fulfill.models import WarehouseFulfill, ShippingCharge
import accountifie.toolkit
from accountifie.toolkit.forms import FileForm
import inventory.apiv1 as inventory_api

from .file_models.UPS import UPSCSVModel
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
        dupes, new_packs, error_cnt, error_msgs = process_ups(file_name_with_timestamp)

        messages.success(request, 'Loaded UPS file: %d new records, \
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
        messages.error(request, 'Could not process the UPS file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))


def process_ups(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    ship_charges, errors = UPSCSVModel.import_data(data=open(incoming_name, 'rU'), skip_rows=6)
    shipper_id = inventory_api.shipper('UPS', {})['id']

    new_recs_ctr = 0
    exist_recs_ctr = 0
    errors_cnt = len(errors)

    for rec in ship_charges:
        rec['shipper_id'] = shipper_id
        rec_obj = None

        if rec_obj:
            # if warehose fulfill object already exists ... skip to next one
            exist_recs_ctr += 1
        else:
            whflf_obj = WarehouseFulfill.objects \
                                        .filter(tracking_number=rec['tracking_number']) \
                                        .first()
            if whflf_obj:
                flf = whflf_obj.fulfillment
                if flf:
                    rec['fulfillment_id'] = flf.id

            new_recs_ctr += 1
            rec_obj = ShippingCharge(**rec)
            rec_obj.save()

    return exist_recs_ctr, new_recs_ctr, errors_cnt, errors
