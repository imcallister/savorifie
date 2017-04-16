import os
from decimal import Decimal

from django.conf import settings

from .file_models.shopify_payouts import ShopifyPayoutCSVModel
from accountifie.common.uploaders.upload_tools import order_upload
from sales.models import Payout, PayoutLine
from accountifie.common.api import api_func
import logging
logger = logging.getLogger('default')


DATA_ROOT = getattr(settings, 'DATA_DIR', os.path.join(settings.ENVIRON_DIR, 'data'))
INCOMING_ROOT = os.path.join(DATA_ROOT, 'incoming')
PROCESSED_ROOT = os.path.join(DATA_ROOT, 'processed')

def upload(request):
    processor = process_shopify_payouts
    return order_upload(request,
                        processor,
                        label=False)


def process_shopify_payouts(file_name):
    incoming_name = os.path.join(INCOMING_ROOT, file_name)
    po_records, errors = ShopifyPayoutCSVModel.import_data(data=open(incoming_name, 'rU'))
    new_recs_ctr = 0
    exist_recs_ctr = 0
    errors_cnt = len(errors)
    
    # payouts are unique by date. create those that do no yet exist
    payout_dates = list(set(r['payout_date'].date() for r in po_records))
    payouts = dict((p.payout_date, p) for p in Payout.objects.filter(payout_date__in=payout_dates))

    for d in [d for d in payout_dates if d not in payouts]:
        po_info = {}
        po_info['channel_id'] = api_func('sales', 'channel', 'SHOPIFY')['id']
        po_info['payout_date'] = d
        po_info['payout'] = Decimal('0')
        po_info['paid_thru_id'] = 'SHOPIFY'
        po = Payout(**po_info)
        po.save()
        payouts[d] = po
    
    payouts_changed = []
    for rec in po_records:
        pol_info = {}
        pol_info['sale'] = rec['sale']
        pol_info['amount'] = rec['amount']
        pol_info['payout'] = payouts.get(rec['payout_date'].date())    
        po_obj = PayoutLine.objects.filter(payout=pol_info['payout']) \
                                   .filter(amount=rec['amount']) \
                                   .filter(sale_id=rec['sale'].id) \
                                   .first()
        if not po_obj:
            PayoutLine(**pol_info).save()
            new_recs_ctr += 1
        else:
            exist_recs_ctr += 1
    
        payouts_changed.append(pol_info['payout'])
    
    for po in list(set(payouts_changed)):
        po.save()

    summary_msg = 'Loaded Shopify payout file: %d new records, %d duplicate records, %d bad rows' \
                                    % (new_recs_ctr, exist_recs_ctr, errors_cnt)
    return summary_msg, errors
