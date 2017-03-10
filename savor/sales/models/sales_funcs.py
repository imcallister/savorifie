
from accountifie.common.api import api_func


def create_external_channel_id(special_sale, channel):
    if special_sale:
        sample_ids = [s['external_channel_id'].lower() for s in api_func('sales', 'external_ids', qstring={'filter': 'sample'})]
        sample_ids = [int(s.replace('sample', '')) for s in sample_ids]

        special_ids = [s['external_channel_id'].lower() for s in api_func('sales', 'external_ids', qstring={'filter': 'special'})]
        special_ids = [int(s.replace('special', '')) for s in special_ids]
                
        used_ids = sample_ids + special_ids

        if len(used_ids) == 0:
            max_id = 0
        else:
            max_id = max(used_ids)
        return 'SPECIAL%d' % (max_id + 1)
    else:
        auto_ids = [s['external_channel_id'] for s in api_func('sales', 'external_ids', qstring={'filter': channel})]
        used_ids = [int(s.replace(channel + '.', '')) for s in auto_ids]
        
        if len(used_ids) == 0:
            max_id = 0
        else:
            max_id = max(used_ids)
        return '%s.%d' % (channel, max_id + 1)


def get_receiveables_account(channel):
        if channel in ['PAMPHOM', 'GROMMET', 'PAPERSO', 'UNCOMMON']:
            return api_func('environment', 'variable', 'GL_ACCOUNTS_RECEIVABLE_TERMS')
        else:
            return api_func('environment', 'variable', 'GL_ACCOUNTS_RECEIVABLE')

def get_shipping_account():
    return api_func('gl', 'account', 'liabilities.curr.accrued.shipping')['id']

def get_giftwrap_account():
    return api_func('gl', 'account', 'equity.retearnings.sales.extra.giftwrap')['id']

def get_salestax_account():
    return api_func('gl', 'account', 'liabilities.curr.accrued.salestax')['id']

def get_discount_account(channel):
    return api_func('gl', 'account', 'equity.retearnings.sales.discounts.%s' % channel)['id']

def get_channelfees_account(channel):
    return api_func('gl', 'account', 'equity.retearnings.opexp.sales.channelfees.%s' % channel)['id']
