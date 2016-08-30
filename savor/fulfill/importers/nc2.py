import os
import pandas as pd
from dateutil.parser import parse
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from ..models import WarehouseFulfill, WarehouseFulfillLine
import accountifie.toolkit
from accountifie.toolkit.forms import FileForm
from accountifie.common.api import api_func

import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')


def order_upload(request):
    form = FileForm(request.POST, request.FILES)

    if form.is_valid():
        upload = request.FILES.values()[0]
        file_name = upload._name
        file_name_with_timestamp = accountifie.toolkit.uploader.save_file(upload)
        dupes, new_packs, missing_ship_codes = process_nc2(file_name_with_timestamp)
        messages.success(request, 'Loaded NC2 file: %d new records and %d duplicate records' % (new_packs, dupes))
        messages.error(request, 'Missing shipping codes: %d ' % (missing_ship_codes))
        context = {}
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        context = {}
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the NC2 file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))


def process_nc2(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    
    # TODO .... using pandas makes it all very ugly
    with open(incoming_name, 'U') as f:
        warehouse_records = pd.read_csv(incoming_name)

    new_recs_ctr = 0
    exist_recs_ctr = 0
    missing_ship_codes = 0

    # any pre-formatting of data here

    def rounder(f, places=2):
        if places==5:
            return Decimal(Decimal(f).quantize(Decimal('.00001'), rounding=ROUND_HALF_UP))
        else:
            return Decimal(Decimal(f).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

    records = []
    for k, v in warehouse_records.groupby('OrderNum'):
        pack_info = {}
        pack_info['warehouse_id'] = api_func('inventory', 'warehouse', 'NC2')['id']

        # have our orders be of form 'SAL.xxxx' or 'TRF.xxxx'
        # for most packs we are using first row
        top_row = v.iloc[0]
        savor_request_id = top_row['OrderNum'].replace('SAL.', '') \
                                              .replace('FLF', '') \
                                              .replace('TRF.', '')

        try:
            pack_info['fulfillment_id'] = savor_request_id
            # set default values
            pack_info['warehouse_pack_id'] = ','.join([str(n) for n in v['ShipNum'].values])
            pack_info['order_date'] = parse(top_row['OrderDate']).date()
            pack_info['request_date'] = parse(top_row['OrderDate']).date()
            pack_info['ship_date'] = parse(top_row['ShipDate']).date()
            pack_info['shipping_name'] = top_row['Name']
            pack_info['shipping_attn'] = top_row['Company']
            pack_info['shipping_zip'] = top_row['Zip']
            pack_info['shipping_country'] = top_row['Country']
            pack_info['ship_email'] = top_row['Email']

            pack_info['tracking_number'] = ','.join([str(n) for n in v['Tracking#'].values])[:90]
            pack_info['weight'] = sum([rounder(w, places=5) for w in v['Weight [Lbs.]'].values])
            pack_info['shipping_cost'] = sum([rounder(w, places=2) for w in v['ShippingCost'].values])
            pack_info['handling_cost'] = sum([rounder(w, places=2) for w in v['HandlingCost'].values])

            ship_code = top_row['ShipMethod']
            SHIP_MAP = {'FEG': 'FEDEX_GROUND', 'PMD': 'USPS_PRIORITY', 'GRND': 'UPS_GROUND'}
            if ship_code not in SHIP_MAP:
                missing_ship_codes += 1
            else:
                pack_info['shipping_type_id'] = api_func('inventory', 'shippingtype', SHIP_MAP[ship_code])['id']

            pack_obj = WarehouseFulfill.objects.filter(warehouse_pack_id=pack_info['warehouse_pack_id']).first()
            if pack_obj:
                # if warehose fulfill object already exists ... skip to next one
                exist_recs_ctr += 1
            else:
                new_recs_ctr += 1
                pack_obj = WarehouseFulfill(**pack_info)
                pack_obj.save()
        except BaseException as e:
            logger.error('NC2 record: failed to load %s. Error: %s' % (savor_request_id, str(e)))

    return exist_recs_ctr, new_recs_ctr, missing_ship_codes
