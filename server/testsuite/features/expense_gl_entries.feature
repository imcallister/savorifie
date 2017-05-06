Feature: Expense generates GL entries
When an Expense object is created
I want transaction lines to be created
So that they can be sent to the backend service

Background: There are accounts and companies and counterparties in the system
    Given there are companies:
        |     id     |  name   | cmpy_type |
        |    TSTCO   | Test Co |   ALO     |

    And there are accounts:
        |    id             |   path                        |
        |    3000           |   liabilities.curr.ap         |
        |    1250           |   assets.curr.prepaidexp      |
        |    3110           |   liabilities.curr.accliab    |
        |    7654           |   equity.opexp.sample         |

    And there are counterparties:
        |    id     |    name        |
        |  TESTCP   |    Test CP     |
    
    And there are environment variables:
        |    key                    |   value   |
        |    GL_ACCOUNTS_PAYABLE    |   3000    |
        |    GL_PREPAID_EXP         |   1250    |
        |    GL_ACCRUED_LIAB        |   3110    |
        |     DEFAULT_COMPANY_ID    |   TSTCO   |
        

@expense_gl
Scenario: Single-date expense creates expected GL entries
    Given a new expense:
        |  company  |  amount   |  account  | expense_date  | counterparty | paid_from |
        |  TSTCO   |  122.21    |  7654     |  2016-1-1     |    TESTCP    |  3000     |
    
    When we calculate the BMO GL entries
    
    Then the lines should be:
        | account   |   amount  |  counterparty  |    date    |  date_end |
        |  7654     |   122.21  |    TESTCP      |  2016-1-1  |           |
        |  3000     |   -122.21 |    TESTCP      |  2016-1-1  |           |

@expense_gl
Scenario: Small multi-date expense creates expected GL entries
    Given a new expense:
        |  company  |  amount   |  account  | start_date  | end_date   | expense_date  | counterparty | paid_from |
        |  TSTCO   |  122.21    |  7654     | 2016-1-1    |  2016-1-31 |  2016-1-1     |    TESTCP    |  3000      |
    
    When we calculate the BMO GL entries
    
    Then the lines should be:
        | account   |   amount  |  counterparty  |    date    |  date_end |
        |  7654     |   122.21  |    TESTCP      |  2016-1-1  |           |
        |  3000     |   -122.21 |    TESTCP      |  2016-1-1  |           |

@expense_gl
Scenario: Large multi-date expense with expense date at start creates expected GL entries
    Given a new expense:
        |  company  |  amount   |  account  | start_date  | end_date   | expense_date  | counterparty |  paid_from |
        |  TSTCO    |  500.1    |  7654     | 2016-1-1    |  2016-1-31 |  2016-1-1     |    TESTCP    |    3000    |
    
    When we calculate the BMO GL entries
    
    Then the lines should be:
        | account   |   amount  |  counterparty  |    date   | date_end   |
        |  7654     |   500.1   |    TESTCP      |  2016-1-1 |  2016-1-31 | 
        |  3000     |   -500.1  |    TESTCP      |  2016-1-1 |            |
        |  1250     |   500.1   |    TESTCP      |  2016-1-1 |            |
        |  1250     |   -500.1  |    TESTCP      |  2016-1-1 | 2016-1-31 | 
