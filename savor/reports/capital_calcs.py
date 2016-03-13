import accountifie.environment.api

def cap_and_subdebt(company_id, dates, query_manager):
    return query_manager.pd_path_balances(company_id, dates, ['equity','liabilities.noncurr.ltdebt.subdebt'])

def non_allowable(company_id, dates, query_manager):
    return query_manager.pd_path_balances(company_id, dates, ['assets.curr.other'])
        
def subdebt(company_id, dates, query_manager):
    return query_manager.pd_path_balances(company_id, dates, ['liabilities.noncurr.ltdebt.subdebt'])

def AI(company_id, dates, query_manager):
    NON_AI_ACCTS = accountifie.environment.api.variable({'name': 'NON_AI_ACCTS'})
    liabs = query_manager.pd_acct_balances(company_id, dates, paths=['liabilities'])
    liabs.fillna(0.0, inplace=True)
    return liabs[~liabs.index.isin(NON_AI_ACCTS)] * (-1.0)