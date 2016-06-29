Feature: Sale generates GL entries
When a Sale object is created
I want two transaction lines to be created
So that they can be sent to the backend service

Background: There are accounts and companies and counterparties in the system
    Given there are companies:
        |     id     |  name   | cmpy_type |
        |    TEST    | Test Co |   ALO     |

    And there are accounts:
        |    id             |   path                        |
        |    1100           |   assets.curr.receivables     |
        |    4000           |liabilities.curr.accrued.shipping|
        |    4001           |equity.retearnings.sales.extra.giftwrap|
        |    4002           |liabilities.curr.accrued.salestax|
        |    1200           |   assets.curr.inv.II101       |
        |    5000           |   equity.sales.gross.II101    |
        |    5100           |   equity.sales.COGS.II101     |
        |    5110           |   equity.sales.samples.press  |
        |    5120           |   equity.sales.discounts      |


    And there are counterparties:
        |        id       |      name       |
        |  SHOPIFY        |    Shopify      |
        |  retail_buyer   |   Retail Buyer  |
        |     press       |     Press       |

    And there are environment variables:
        |    key                    |   value   |
        |    GL_ACCOUNTS_PAYABLE    |   3000    |
        |    GL_PREPAID_EXP         |   1250    |
        |    GL_ACCRUED_LIAB        |   3110    |
        |   GL_ACCOUNTS_RECEIVABLE  |   1100    |
    
    And there are channels:
        |    counterparty   |
        |      SHOPIFY      |

    And there are warehouses:
        | id |    description   |  label  |
        |  1 |    whouse1       |   WH1   |

    And there are productlines:
        | id |    description   |  label  |
        |  1 |  First Line      |   PL1   |

    And there are products:
        | id |    description   |  label   |
        |  1 |  Products        |   PR001  |

    And there are inventoryitems:
        | id | description |    label   |  productline  |   master_sku  |
        |  1 |   invitem01 |     II01   |      1        |    msku0001   |

    And there are skuunits:
        |  inv_item  |  sku   | quantity |
        |    II01    | PR001  |    1     |

    And there are shipments:
        | id   |  arrival_date  |  description   |  label | warehouse |
        |  1   |   2016-01-01   |    first       |   SH1  |    1      |

    And there are shipmentlines:
        |   id   | inv_item |  cost   |  quantity | shipment |
        |  1     |   II01   |    25   |   100     |   SH1    |



Scenario: Regular Sale GL entries
    Given a new sale:
        |  id  |  company  |  channel   |  customer_code  | shipping_charge |
        |   1  |  TEST     |  SHOPIFY   |  retail_buyer   |      0          |
    And new unitsales:
        |   id  |   sale   |    sku    |  quantity  | unit_price |
        |   1   |    1     |   PR001   |     1      |    80      |
    And a COGSassignment:
        | shipment_line | unitsale  | quantity |
        |     1        |     1     |     1    |
    
    When we calculate the BMO GL entries
    
    Then the lines should be:
        | account   |   amount  |  counterparty  |
        |  1100     |   80.0    |    TESTCP      |
        |  1200     |   -25.0   |    TESTCP      | 
        |  5000     |   -80     |    TESTCP      |
        |  5100     |   25.0    |    TESTCP      |


Scenario: Free sample. Savor pays all shipping costs
    Given a new sale:
        |  id  |  company  |  channel   |  customer_code | counterparty |  sample | shipping_charge |
        |   1  |  TEST     |  SHOPIFY   |  press         |     TESTCP   |   True  |       0         |
    And new unitsales:
        |   id  |   sale   |    sku    |  quantity  | unit_price |
        |   1   |    1     |   PR001   |     1      |    80      |
    And a COGSassignment:
        | shipment_line | unitsale  | quantity |
        |     1        |     1     |     1    |
    
    When we calculate the BMO GL entries
    
    Then the lines should be:
        | account   |   amount  |  counterparty  |
        |  1200     |   -25.0   |    press       | 
        |  5110     |   25.0    |    press       |

Scenario: Sale with Discount GL entries
    Given a new sale:
        |  id  |  company  |  channel   |  customer_code  | counterparty | discount | shipping_charge  |
        |   1  |  TEST     |  SHOPIFY   |  retail_buyer   |     TESTCP   |   10     |       0          |
    And new unitsales:
        |   id  |   sale   |    sku    |  quantity  | unit_price |
        |   1   |    1     |   PR001   |     1      |    80      |
    And a COGSassignment:
        | shipment_line | unitsale  | quantity |
        |     1    |     1     |     1    |
    
    When we calculate the BMO GL entries
    
    Then the lines should be:
        | account   |   amount  |  counterparty     |
        |  1100     |   70.0    |    retail_buyer   |
        |  1200     |   -25.0   |    retail_buyer   | 
        |  5000     |   -80     |    retail_buyer   |
        |  5100     |   25.0    |    retail_buyer   |
        |  6000     |   10      |    retail_buyer   |


