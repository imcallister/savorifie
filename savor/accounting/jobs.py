"Re-saves all things which might produce GL transactions."
import logging
import pandas as pd

from django.http import HttpResponseRedirect

from accountifie.celery import background_task
import savor.accounting.apiv1 as acctg_api
import inventory.apiv1 as inv_api
from accounting.models import COGSAssignment


logger = logging.getLogger('default')

def fifo_assign(unit_sale_id, to_assign):
    for ii, qty in to_assign.iteritems():
        available = acctg_api.fifo_available_shipmentlines({}, ii)
        if qty != 0:
            rmg_qty = qty
            while rmg_qty != 0:
                sl = available.pop(0)
                
                fifo_info = {}
                assgn_qty = min(rmg_qty, sl['available'])
                fifo_info['unit_sale_id'] = unit_sale_id
                fifo_info['quantity'] = assgn_qty
                fifo_info['shipment_line_id'] = sl['id']
                rmg_qty -= assgn_qty
                COGSAssignment(**fifo_info).save()
                if len(available) == 0: # no more shipment lines left
                    rmg_qty = 0
    return


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
    
    return
