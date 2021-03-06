from django.conf.urls import url
import UPS
import NC2
import Franklin
import FRB
import mcard
import IFS_monthly
import bulk_shipping
import buybuy
import AMZN_orders
import shopify_payouts
import amazon_payouts
import FBA
import shopify_orders
import AMZN_PMTS_payouts
import paypal_payouts


urlpatterns = [
    url(r'importers/nc2_upload/$', NC2.upload),
    url(r'importers/frank_upload/$', Franklin.upload),
    url(r'importers/upload/bulk_shipping/$', bulk_shipping.upload),
    url(r'importers/upload/ups/$', UPS.upload),
    url(r'importers/upload/frb/$', FRB.upload),
    url(r'importers/upload/mcard/$', mcard.upload),
    url(r'importers/upload/IFSmonthly/$', IFS_monthly.upload),
    url(r'importers/upload/buybuy/$', buybuy.upload),
    url(r'importers/upload/AMZN_orders/$', AMZN_orders.upload),
    url(r'importers/upload/shopify_payouts/$', shopify_payouts.upload),
    url(r'importers/upload/amazon_payouts/$', amazon_payouts.upload),
    url(r'importers/upload/FBA/$', FBA.upload),
    url(r'importers/upload/shopify_orders/$', shopify_orders.upload),
    url(r'importers/upload/AMZN_PMTs/$', AMZN_PMTS_payouts.upload),
    url(r'importers/upload/paypal/$', paypal_payouts.upload),
    url(r'importers/upload/missing_amazon/$', FBA.missing_amazon),
]
