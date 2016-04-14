from accountifie.common.api import api_func
from accountifie.query.query_manager import pd_path_balances


def cap_and_subdebt(company_id, dates, query_manager):
    return pd_path_balances(company_id, dates, ['equity','liabilities.noncurr.ltdebt.subdebt'])

def non_allowable(company_id, dates, query_manager):
    return pd_path_balances(company_id, dates, ['assets.curr.other'])
        
def subdebt(company_id, dates, query_manager):
    return pd_path_balances(company_id, dates, ['liabilities.noncurr.ltdebt.subdebt'])

def AI(company_id, dates, query_manager):
    NON_AI_ACCTS = api_func('environment', 'variable', 'NON_AI_ACCTS')
    liabs = pd_acct_balances(company_id, dates, paths=['liabilities'])
    liabs.fillna(0.0, inplace=True)
    return liabs[~liabs.index.isin(NON_AI_ACCTS)] * (-1.0)