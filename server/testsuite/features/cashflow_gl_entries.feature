Feature: Cashflow generates GL entries
When a Cashflow object is created
I want two transaction lines to be created
So that they can be sent to the backend service

Background: There are accounts and companies and counterparties in the system
    Given there are companies:
        |     id     |  name   | cmpy_type |
        |    TEST    | Test Co |   ALO     |

    And there are accounts:
        |    id             |   path                        |
        |    1001           |   assets.curr.cash.checking   |
        |    1002           |   assets.curr.cash.saving     |
        |    1004           |   assets.curr.cash.mmkt       |
        |    3000           |   liabilities.curr.ap         |

    And there are counterparties:
        |    id     |    name        |
        |  TESTCP   |    Test CP     |
        |  DEPO01    |   Depositary1  |
    
    And there are external accounts:
        |    account_id     |   cp        |  company  |
        |    1001           |   DEPO01    |  TEST     |
        |    1002           |   DEPO01    |  TEST     |
        |    1004           |   DEPO01    |  TEST     |

        

Scenario Outline: GL entries
    When a new cashflow from "<ext_account>" and "<amount>" and "<post_date>" and "<counterparty>"
    Then I see "<num_lines>" GL lines

    Examples:
        |  ext_account  |  amount   |  post_date  | counterparty | num_lines |
        |  1001         |  122.21   |  2016-02-02 |     TESTCP   |    2      |
        |  1002         |  987.21   |  2016-02-02 |     TESTCP   |    2      |
        |  1004         |  106.21   |  2016-02-02 |     TESTCP   |    2      |


Scenario: GL entries2
    Given a new cashflow:
        |  ext_account  |  amount   |  post_date  | counterparty | num_lines |
        |  1001         |  122.21   |  2016-02-02 |     TESTCP   |    2      |
    When we calculate the BMO GL entries
    Then the lines should be:
        | account   |   amount  |  counterparty  |   date     |  date_end  |
        |  1001     |   122.21  |    TESTCP      | 2016-02-02 |            |
        |  3000     |   -122.21 |    TESTCP      | 2016-02-02 |            |

