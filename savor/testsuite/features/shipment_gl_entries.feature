Feature: A Shipment generates GL entries
When a Shipment Line object is created
I want two transaction lines to be created
So that they can be sent to the backend service

Background: There are accounts and companies and counterparties in the system
    Given there are companies:
        |     id     |  name   | cmpy_type |
        |    TEST    | Test Co |   ALO     |

    And there are accounts:
        |    id     |           path                                 |
        |    1200   |   assets.curr.inventory.PL1.II01               |
        |    1201   |   assets.curr.inventory.PL1.II02               |
        |    3000   |         liabilities.curr.ap                    |
        

    And there are counterparties:
        |        id     |      name       |
        |      MANUF1   |   Factory1      |

    And there are environment variables:
        |    key                    |   value   |
        |    GL_ACCOUNTS_PAYABLE    |   3000    |
        |  DEFAULT_COMPANY_ID       |   TEST    |
        
    
    And there are warehouses:
        |    description   |  label  |
        |    whouse1       |   WH1   |

    And there are productlines:
        |    description   |  label  |
        |  First Line      |   PL1   |

    
    And there are inventoryitems:
        | description |    label   |  productline  |   master_sku  |
        |   invitem01 |     II01   |      PL1      |    msku0001   |
        |   invitem02 |     II02   |      PL1      |    msku0002   |


@shipline_gl
Scenario: Shipment Line GL entries
    Given there are shipments:
        |  arrival_date  |  description   |  label | warehouse |  sent_by   |
        |   2016-01-01   |    first       |   SH1  |    WH1    |   MANUF1   |

    And a shipmentline is booked:
        | inv_item |  cost   |  quantity | shipment |
        |   II01   |    25   |   100     |   SH1    |

    
    When we calculate the BMO GL entries
    
    Then the lines should be:
        | account   |   amount  | counterparty |    date    |  date_end |
        |  1200     |    2500   |   MANUF1     | 2016-01-01 |           |
        |  3000     |   -2500   |   MANUF1     | 2016-01-01 |           |

