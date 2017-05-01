from decimal import Decimal
import logging
import itertools
import copy

from django.db import models


import accountifie.gl.bmo
from accountifie.toolkit.utils import get_default_company

import sales_funcs
from sale_gl_mixin import SaleGLMixin

DZERO = Decimal('0')

logger = logging.getLogger('default')


SPECIAL_SALES = (
    ('press', 'Press Sample'),
    ('consignment', 'Consignment'),
    ('prize', 'Gift/Prize'),
    ('retailer', 'Retailer Sample'),
    ('payment', 'Payment'),
)

class Sale(models.Model, accountifie.gl.bmo.BusinessModelObject, SaleGLMixin):
    company = models.ForeignKey('gl.Company', default=get_default_company)

    channel = models.ForeignKey('sales.Channel', blank=True, null=True)
    sale_date = models.DateField()
    external_channel_id = models.CharField(max_length=50, unique=True,
                                           blank=True, null=True,
                                           help_text='If no ID, leave blank for system-generated ID')
    external_routing_id = models.CharField(max_length=50, blank=True, null=True)
    checkout_id = models.CharField(max_length=50, blank=True, null=True)
    special_sale = models.CharField(max_length=20, choices=SPECIAL_SALES, blank=True, null=True)
    
    paid_thru = models.ForeignKey('gl.Counterparty', blank=True, null=True,
                                  related_name='paid_thru',
                                  limit_choices_to={'id__in': ['SHOPIFY', 'PAYPAL', 'AMZN', 'AMZN_PMTS', 'BBB']})
    
    customer_code = models.ForeignKey('gl.Counterparty', blank=True, null=True)
    notification_email = models.EmailField(max_length=254, blank=True, null=True)
    memo = models.TextField(null=True, blank=True)

    gift_wrapping = models.BooleanField(default=False)
    gift_wrap_fee = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'))
    gift_message = models.TextField(null=True, blank=True)

    shipping_name = models.CharField(max_length=100, blank=True, null=True)
    shipping_company = models.CharField(max_length=100, blank=True, null=True)
    shipping_address1 = models.CharField(max_length=100, blank=True, null=True)
    shipping_address2 = models.CharField(max_length=100, blank=True, null=True)
    shipping_city = models.CharField(max_length=50, blank=True, null=True)
    shipping_zip = models.CharField(max_length=20, blank=True, null=True)
    shipping_province = models.CharField(max_length=30, blank=True, null=True)
    shipping_country = models.CharField(max_length=30, blank=True, null=True)
    shipping_phone = models.CharField(max_length=30, blank=True, null=True)

    short_code = 'SALE'

    def __unicode__(self):
        if self.channel.counterparty.id == 'SAV':
            return self.external_channel_id
        else:
            return '%s: %s' % (self.channel.counterparty.id, self.external_channel_id)

    class Meta:
        app_label = 'sales'
        db_table = 'sales_sale'

    def save(self, update_gl=True):
        if not self.external_channel_id:
            self.external_channel_id = sales_funcs.create_external_channel_id(self.special_sale, str(self.channel))

        if update_gl:
            self.update_gl()

        models.Model.save(self)
        
    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)


    @property
    def channel_name(self):
        return str(self.channel)

    @property
    def items_string(self):
        items = [(k, v) for k, v in self.inventory_items.iteritems()]
        items = sorted(items, key=lambda x: x[0])
        return ','.join(['%s %s' % (i[1], i[0]) for i in items])

    @property
    def inventory_items(self):
        u_items = [u.inventory_items().items() for u in self.unit_sale.all()]
        all_u_items = list(itertools.chain.from_iterable(u_items))
        g = itertools.groupby(sorted(all_u_items, key=lambda x: x[0]),
                              key=lambda x:x[0])
        return dict((k, sum([i[1] for i in list(v)])) for k, v in g)

    @property
    def fulfilled_items(self):
        items = [(str(l.inventory_item), l.quantity) for f in self.fulfillments.all() \
                                                     for l in f.fulfill_lines.all()]
        g = itertools.groupby(sorted(items, key=lambda x: x[0]), key=lambda x: x[0])
        fulf = dict((k, sum([i[1] for i in list(v)])) for k, v in g if v > 0)
        if len(fulf) > 0:
            return fulf
        else:
            return None

    @property
    def unfulfilled_items(self):
        d1 = self.inventory_items
        d2 = self.fulfilled_items
        if d2:
            unf = {k: int(d1.get(k, 0)) - int(d2.get(k, 0)) for k in set(d1) | set(d2)}
            unf = dict((k, v) for k, v in unf.iteritems() if v != 0)
            if len(unf) > 0:
                return unf
            else:
                return None
        else:
            return d1

    @property
    def label(self):
        return str(self)

    def gross_sale_proceeds(self):
        return sum([v for k, v in self.get_unit_sales().iteritems()])


    def total_sales_tax(self):
        tax_amts = self.get_sales_taxes()
        return Decimal(sum([v for k, v in tax_amts.iteritems()]))

    def total_receivable(self, incl_ch_fees=True):
        total = self.gross_sale_proceeds()
        adjusts = self.proceedsadjustment_sale \
                       .filter(adjust_type__in=['GIFTWRAP_FEES', 'DISCOUNT', 'SHIPPING_CHARGE']) \
                       .aggregate(models.Sum('amount')).get('amount__sum', Decimal('0'))
        if adjusts:
            total += adjusts
        
        tax_amts = self.get_sales_taxes()
        total += sum([v for k, v in tax_amts.iteritems()])
        
        
        channel_fees =  self.proceedsadjustment_sale \
                            .filter(adjust_type='CHANNEL_FEES') \
                            .aggregate(models.Sum('amount')).get('amount__sum', Decimal('0'))
        
        if channel_fees:
            total -= channel_fees
            
        return total

    def taxable_proceeds(self):
        total = self.gross_sale_proceeds()
        total += self.proceedsadjustment_sale \
                     .filter(adjust_type__in=['GIFTWRAP_FEES', 'DISCOUNT', 'SHIPPING_CHARGE']) \
                     .aggregate(models.Sum('amount'))['amount__sum']
        return total

    def payee(self):
        if self.paid_thru:
            return self.paid_thru
        elif self.channel.label == 'SAV':
            return self.customer_code
        else:
            return self.channel.counterparty

    
    def get_sales_taxes(self):
        sales_taxes = self.sales_tax.all()
        tax_collectors = list(set([t.collector.entity for t in sales_taxes]))
        tax_amts = dict((p, 0) for p in tax_collectors)
        for t in sales_taxes:
            tax_amts[t.collector.entity] += Decimal(t.tax)
        return tax_amts


    def get_unit_sales(self):
        unit_sales = self.unit_sale.all()
        skus = list(set([x.sku for x in unit_sales]))
        
        sale_amts = dict((s, 0) for s in skus)
        for s in unit_sales:
            sale_amts[s.sku] += Decimal(s.quantity) * Decimal(s.unit_price)
        return sale_amts

    
    def get_gl_transactions(self):
        base_tran = dict(company=self.company,
                         bmo_id='%s.%s' % (self.short_code, self.id),
                         lines=[]
                       )

        if self.special_sale == 'payment':
            tran = dict((k, v) for k, v in base_tran.iteritems())
            tran['date'] = self.sale_date
            tran['comment'] = "Payment - %s: %s" % (self.channel, self.external_channel_id)
            tran['trans_id'] = '%s.%s.%s' % (self.short_code, self.id, 'SALE')
            tran['lines'] += self.get_payment_lines()
            return [tran]
        elif self.special_sale:
            tran = dict((k, v) for k, v in base_tran.iteritems())
            tran['date'] = self.sale_date
            tran['comment'] = "%s - %s: %s" % (self.special_sale, self.channel, self.external_channel_id)
            tran['trans_id'] = '%s.%s.%s' % (self.short_code, self.id, 'SALE')
            tran['lines'] += self.get_specialsale_lines()
            return [tran]
        else:
            trans = []

            for dt in self.get_all_dates():
                if dt:
                    tran = copy.deepcopy(base_tran)
                    tran['date'] = dt
                    
                    if dt == self.sale_date:
                        tran['comment'] = "%s: %s" % (self.channel, self.external_channel_id)
                        tran['trans_id'] = '%s.%s.%s' % (self.short_code, self.id, 'SALE')
                    else:
                        tran['comment'] = "%s: %s.ADJUST:%s" % (self.channel, self.external_channel_id, dt.strftime('%d%b%y'))
                        tran['trans_id'] = '%s.%s.ADJ%s' % (self.short_code, self.id, dt.strftime('%d%b%y'))
                    
                    tran['lines'] += self.get_grosssales_lines(dt)
                    tran['lines'] += self.get_salestax_lines(dt)
                    tran['lines'] += self.get_adjustment_lines(dt)
                    tran['lines'] += self.get_COGS_lines(dt)
                    # acctr receivable should be sum of all the above lines
                    tran['lines'] += self.get_acctrec_lines(tran['lines'])

                    trans.append(tran)
                
            return trans
