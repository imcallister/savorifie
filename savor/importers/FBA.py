import json
import sys
import traceback

from django.http import JsonResponse

from amzn_utilities import _create_sale, _save_objects, _FBA_start_date
from .thirdparty_apis.amazon_sellercentral import load_orders, order_details, get_order
from sales.models import Sale


import logging
logger = logging.getLogger('default')


def missing_amazon(request):
    try:
        summary_msg, error_msgs = amazon_order(request.user.username, request.body)
        return JsonResponse({'summary': summary_msg, 'errors': error_msgs})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        msg = 'FBA fill-missing failed on %s, %s' % (exc_type, exc_value)
        return JsonResponse({'summary': msg, 'errors': []})


def upload(request):
    try:
        summary_msg, error_msgs = load_FBA(request.user.username)
        return JsonResponse({'summary': summary_msg, 'errors': error_msgs})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        msg = 'FBA upload failed on %s, %s' % (exc_type, exc_value)
        return JsonResponse({'summary': msg, 'errors': []})


def amazon_order(user, data):
    errors = []
    order_id = json.loads(data).get('input_value')
    if Sale.objects.filter(external_channel_id=order_id).count() > 0:
        msg = '%s already exists' % order_id
        return msg, errors
    else:
        try:
            s, us = _create_sale(get_order(order_id), order_details(order_id))
            _save_objects(s, us, 'AFN')
            logger.info('%s saved AMZN order %s' % (user, order_id))
            msg = '%s created order %s' % (user, order_id)
        except:
            logger.exception('%s failed to save order and/or fulfillment for AMZN order %s' % (user, object_id))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            msg = exc_value
        return msg, errors


def load_FBA(user, from_date=None):
    if not from_date:
        from_date = _FBA_start_date()

    orders = load_orders(from_date)
    orders_dict = dict((o.get('AmazonOrderId'), o) for o in orders)

    FBA_ids = [o.get('AmazonOrderId') for o in orders]
    existing_ids = [s['external_channel_id'] for s in Sale.objects.filter(external_channel_id__in=FBA_ids).values('external_channel_id')]

    new_ids = [o for o in FBA_ids if o not in existing_ids]
    cmplt_new_ids = [o for o in new_ids if orders_dict.get(o).get('OrderStatus') != 'Pending']
    new_order_ctr = 0
    bad_order_ctr = 0
    errors = []

    for o in cmplt_new_ids:
        try:
            od = order_details(o)
        except:
            logger.exception('Failed to get order details for AMZN order %s' % o)

        sale, unitsales = _create_sale(orders_dict.get(o), od)

        try:
            _save_objects(sale, unitsales, orders_dict.get(o).get('FulfillmentChannel'))
            logger.info('%s saved AMZN order %s' % (user, o))
            new_order_ctr += 1
        except:
            logger.exception('%s failed to save order and/or fulfillment for AMZN order %s' % (user, o))
            bad_order_ctr += 1

    summary_msg = ('Loaded FBA orders: %d new orders, %d bad orders'
                   % (new_order_ctr, bad_order_ctr))
    return summary_msg, errors
