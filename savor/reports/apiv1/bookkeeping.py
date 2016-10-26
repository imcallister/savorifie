from base.models import Cashflow, CreditCardTrans
from fulfill.models import ShippingCharge
from sales.models import ChannelPayouts



def last_uploads(qstring):
    output = []
    FRB = Cashflow.objects.all() \
                          .order_by('-post_date') \
                          .first() \
                          .post_date
    output.append({'Upload': 'First Republic', 'Last Upload': FRB})
    
    citi = CreditCardTrans.objects.all() \
                                  .order_by('-post_date') \
                                  .first() \
                                  .post_date
    output.append({'Upload': 'Citi Credit Card', 'Last Upload': citi})

    UPS = ShippingCharge.objects.filter(shipper__company_id='UPS') \
                                .order_by('-ship_date') \
                                .first() \
                                .ship_date
    output.append({'Upload': 'UPS', 'Last Upload': UPS})

    shopify = ChannelPayouts.objects.filter(channel__counterparty_id='SHOPIFY') \
                                    .order_by('-payout_date') \
                                    .first() \
                                    .payout_date
    output.append({'Upload': 'Shopify Payouts', 'Last Upload': shopify})

    return output
