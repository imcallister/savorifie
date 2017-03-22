"Re-saves all things which might produce GL transactions."
import logging
import pandas as pd

from django.http import HttpResponseRedirect

from accountifie.celery import background_task
import apiv1 as acctg_api
import inventory.apiv1 as inv_api
from models import COGSAssignment
from sales.models import Sale


logger = logging.getLogger('default')


def assign_FIFO(request):
    task_name = 'assign-FIFO'
    task_id = background_task(task=task_name, calc=_assign_FIFO_job).id
    return HttpResponseRedirect('/tasks/list/')



def _assign_FIFO_job(*args, **kwargs):

    # 1 get list of all COGS to be assigned sorted by data
    to_do = sorted(acctg_api.fifo_unassigned({}), key=lambda x: x['id'])
    
    # 2 get an order list of FIFO's available
    available =  pd.DataFrame(acctg_api.fifo_available({})).sort_index(by='arrival_date')
    
    #3 loop thru the COGS needed and pull from FIFO as necessary using oldest first
    new_fifo_list = []
    for u in to_do:
        for item, qty in u['unassigned'].iteritems():
            if qty > 0:
                rmg_qty = qty
                for i in available.index:
                    if available.loc[i, item] > 0:
                        use_cnt = min(available.loc[i, item], rmg_qty)
                        new_fifo_list.append({'order': available.loc[i, 'order'],
                                              'item': item,
                                              'qty': use_cnt,
                                              'unit_sale': u['id'],
                                              'sale': u['sale']})
                        available.loc[i, item] -= use_cnt
                        rmg_qty -= use_cnt
                        if rmg_qty == 0:
                            break
            elif qty < 0: # returns
                for i in available.index:
                    if available.loc[i, item] > 0: # active order
                        new_fifo_list.append({'order': available.loc[i, 'order'],
                                              'item': item,
                                              'qty': qty,
                                              'unit_sale': u['id'],
                                              'sale': u['sale']})
                        break

    # 4 get all the shipment lines that we will need
    all_shipments = dict((sl['unit_label'] + sl['shipment_label'], sl['id']) for sl in inv_api.shipmentline({}))
    # 5 save the COGS assignments
    for new_fifo in new_fifo_list:
        flds = {}
        flds['shipment_line_id'] = all_shipments[new_fifo['item'] + new_fifo['order']]
        flds['unit_sale_id'] = new_fifo['unit_sale']
        flds['quantity'] = new_fifo['qty']
        COGSAssignment(**flds).save()
    # 6 force a gl entry calc for all affected Sale objects
    for sale_id in set([u['sale'] for u in new_fifo_list]):
        Sale.objects.get(id=sale_id).update_gl()
    return
