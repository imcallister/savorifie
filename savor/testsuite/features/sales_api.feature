Feature: Sales api returns list of sales
When a Sales object is created
I want the sales api ro return two dictionaries
So that they can be used in reporting

Background: There are accounts and companies and counterparties in the system
    Given there are companies:
        |     id     |  name   | cmpy_type |
        |    TEST    | Test Co |   ALO     |

    And there are accounts:
        |    id     |           path                                 |
        |    1100   |   assets.curr.receivables                      |
        |    1200   |   assets.curr.inventory.PL1.II01               |
        |    4000   |   liabilities.curr.accrued.shipping            |
        |    4001   |  equity.retearnings.sales.extra.giftwrap       |
        |    4002   |    liabilities.curr.accrued.salestax           |
        |    5000   |   equity.retearnings.sales.gross.SHOPIFY.PL1   |
        |    5100   |   equity.retearnings.sales.COGS.SHOPIFY.PL1    |
        |    5110   |   equity.retearnings.sales.samples.press       |
        |    5120   |   equity.retearnings.sales.discounts.SHOPIFY   |


    And there are counterparties:
        |        id       |      name       |
        |  SHOPIFY        |    Shopify      |
        |  retail_buyer   |   Retail Buyer  |
        |     press       |     Press       |
        |     MANUF1      |    Factory1     |

    And there are environment variables:
        |    key                    |   value   |
        |    GL_ACCOUNTS_PAYABLE    |   3000    |
        |    GL_PREPAID_EXP         |   1250    |
        |    GL_ACCRUED_LIAB        |   3110    |
        |   GL_ACCOUNTS_RECEIVABLE  |   1100    |
        |        GL_INVENTORY       |   1500    |
        |     DEFAULT_COMPANY_ID    |   TEST    |
    
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
        |  1 |   invitem01 |     II01   |      PL1      |    msku0001   |

    And there are skuunits:
        |  inv_item  |  sku   | quantity | rev_percent |
        |    II01    | PR001  |    1     |   100       |

    And there are shipments:
        |  arrival_date  |  description   |  label | warehouse |  sent_by   |
        |   2016-01-01   |    first       |   SH1  |    WH1    |   MANUF1   |

    And there are shipmentlines:
        | inv_item |  cost   |  quantity | shipment |
        |   II01   |    25   |   100     |   SH1    |



Scenario: Regular Sale api call
    Given a sale exists:
        |  external_channel_id  |  company  |  channel   |  customer_code  | shipping_charge | sale_date   |
        |      SHOPIFY123       |  TEST     |  SHOPIFY   |  retail_buyer   |      0          |  2016-03-20 |
    And unitsales exist:
        |   id  |    sale      |    sku    |  quantity  | unit_price |
        |   1   | SHOPIFY123   |   PR001   |     1      |    80      |
    
    When we call the base.sale api
    
    Then the api results should be:
        | account   |   amount  |  counterparty  |    date    |  date_end |
        |  1100     |   80.0    |    SHOPIFY     | 2016-03-20 |           |
        |  1200     |   -25.0   | retail_buyer   | 2016-03-20 |           |
        |  5000     |   -80     | retail_buyer   | 2016-03-20 |           |
        |  5100     |   25.0    | retail_buyer   | 2016-03-20 |           |
