import os
from decimal import Decimal
import pandas as pd
from dateutil.parser import parse

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from inventory.models import WarehouseFulfill, WarehouseFulfillLine
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
        dupes, new_packs, missing_ship_codes = process_thoroughbred(file_name_with_timestamp)
        messages.success(request, 'Loaded thoroughbred file: %d new records and %d duplicate records' % (new_packs, dupes))
        messages.error(request, 'Missing shipping types: %d ' % (missing_ship_codes))
        context = {}
        #return render_to_response('base/uploaded.html', context, context_instance=RequestContext(request))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        context = {}
        context.update({'file_name': request.FILES.values()[0]._name, 'success': False, 'out': None, 'err': None})
        messages.error(request, 'Could not process the shopify file provided, please see below')
        return render_to_response('uploaded.html', context, context_instance=RequestContext(request))


def process_thoroughbred(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    with open(incoming_name, 'U') as f:
        warehouse_records = pd.read_csv(incoming_name)

    new_recs_ctr = 0
    exist_recs_ctr = 0
    missing_ship_codes = 0

    # any pre-formatting of data here

    records = []
    for k, v in warehouse_records.groupby('ORDER_NO'):
        pack_info = {}
        pack_info['warehouse_id'] = api_func('inventory', 'warehouse', 'MICH')['id']

        # have our orders be of form 'SAL.xxxx' or 'TRF.xxxx'
        # for most packs we are using first row
        top_row = v.iloc[0]
        savor_request_id = top_row['CUST_PO'].replace('SAL.', '') \
                                             .replace('FLF', '') \
                                             .replace('TRF.', '')

        try:
            pack_info['fulfillment_id'] = savor_request_id
            # set default values
            pack_info['warehouse_pack_id'] = k
            pack_info['order_date'] = parse(top_row['ORDER_DATE']).date()
            pack_info['request_date'] = parse(top_row['REQUEST_DT']).date()
            pack_info['ship_date'] = parse(top_row['SHIP_DT']).date()
            pack_info['shipping_name'] = top_row['SHIP_NAME']
            pack_info['shipping_attn'] = top_row['SHIP_ATTN']
            pack_info['shipping_address1'] = top_row['SHIP_ADDR1']
            pack_info['shipping_address2'] = top_row['SHIP_ADDR2']
            pack_info['shipping_address3'] = top_row['SHIP_ADDR3']
            pack_info['shipping_city'] = top_row['SHIP_CITY']
            pack_info['shipping_province'] = top_row['SHIP_STATE']
            pack_info['shipping_zip'] = top_row['SHIP_ZIPCODE']
            pack_info['shipping_country'] = top_row['SHIP_COUNTRY']
            pack_info['shipping_phone'] = top_row['SHIPTO_RECIP_PHONE']

            pack_info['ship_email'] = top_row['EMAIL']
            pack_info['tracking_number'] = top_row['TRACK_NO']

            ship_code = top_row['SHIPVIA_CD']
            SHIP_MAP = {'R02': 'FEDEX_GROUND', 'U11': 'UPS_GROUND'}
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

                for idx in v.index:
                    pack_line = {}
                    pack_line['quantity'] = v.loc[idx, 'QTY_ORDER']
                    pack_line['inventory_item_id'] = api_func('inventory', 'inventoryitem', v.loc[idx, 'ITEM_NO'])['id']
                    pack_line['warehouse_fulfill'] = pack_obj
                    line_obj = WarehouseFulfillLine(**pack_line)
                    line_obj.save()
        except:
            logger.error('Thoroughbred record: failed to load %s' % savor_request_id)

    return exist_recs_ctr, new_recs_ctr, missing_ship_codes
