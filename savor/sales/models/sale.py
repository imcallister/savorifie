from django.utils.safestring import mark_safe
from decimal import Decimal
import logging
import itertools

from django.db import models

from simple_history.models import HistoricalRecords

import accountifie.gl.bmo
from accountifie.toolkit.utils import get_default_company
from accountifie.common.api import api_func
from accountifie.gl.models import Account

import sales_funcs

DZERO = Decimal('0')

logger = logging.getLogger('default')


SPECIAL_SALES = (
    ('press', 'Press Sample'),
    ('consignment', 'Consignment'),
    ('prize', 'Gift/Prize'),
    ('retailer', 'Retailer Sample'),
    ('payment', 'Payment'),
)

class Sale(models.Model, accountifie.gl.bmo.BusinessModelObject):
    company = models.ForeignKey('gl.Company', default=get_default_company)

    channel = models.ForeignKey('sales.Channel', blank=True, null=True)
    sale_date = models.DateField()
    external_channel_id = models.CharField(max_length=50, unique=True,
                                           blank=True, null=True,
                                           help_text='If no ID, leave blank for system-generated ID')
    external_routing_id = models.CharField(max_length=50, blank=True, null=True)
    special_sale = models.CharField(max_length=20, choices=SPECIAL_SALES, blank=True, null=True)
    is_return = models.BooleanField(default=False)

    shipping_charge = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal(0))
    channel_charges = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal(0))
    paid_thru = models.ForeignKey('gl.Counterparty', blank=True, null=True,
                                  related_name='paid_thru',
                                  limit_choices_to={'id__in': ['SHOPIFY', 'PAYPAL', 'AMZN', 'AMZN_PMTS']})
    discount = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    discount_code = models.CharField(max_length=50, blank=True, null=True)

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

    history = HistoricalRecords()
    short_code = 'SALE'

    def __unicode__(self):
        if self.channel.counterparty.id == 'SAV':
            return self.external_channel_id
        else:
            return '%s: %s' % (self.channel.counterparty.id, self.external_channel_id)

    class Meta:
        app_label = 'sales'
        db_table = 'base_sale'

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


    def total_sales_tax(self):
        tax_amts = self.get_sales_taxes()
        return Decimal(sum([v for k, v in tax_amts.iteritems()]))

    def total_receivable(self, incl_ch_fees=True):
        total = self.gross_sale_proceeds()
        if self.discount:
            total -= Decimal(self.discount)
        if self.shipping_charge:
            total += Decimal(self.shipping_charge)
        if self.gift_wrap_fee:
            total += Decimal(self.gift_wrap_fee)
        
        tax_amts = self.get_sales_taxes()
        total += sum([v for k, v in tax_amts.iteritems()])
        
        if incl_ch_fees:
            total -= self.channel_charges
        return total

    def taxable_proceeds(self):
        total = self.gross_sale_proceeds()
        if self.discount:
            total -= Decimal(self.discount)
        if self.shipping_charge:
            total += Decimal(self.shipping_charge)
        if self.gift_wrap_fee:
            total += Decimal(self.gift_wrap_fee)
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

    def gross_sale_proceeds(self):
        return sum([v for k, v in self.get_unit_sales().iteritems()])


    

    def get_payment_lines(self):
        channel_id = self.channel.counterparty.id
        amount = self.total_receivable(incl_ch_fees=False)
        accts_rec = sales_funcs.get_receiveables_account(channel_id)
        channel_fees_acct = sales_funcs.get_channelfees_account(channel_id)

        lines = []

        lines.append((accts_rec, -amount, self.customer_code, []))
        lines.append((accts_rec, amount - Decimal(self.channel_charges), self.payee(), []))
        if self.channel_charges > 0:
            lines.append((channel_fees_acct,
                          Decimal(self.channel_charges),
                          channel_id, []))
        return lines

    def get_specialsale_lines(self):
        lines = []
        sample_exp_acct = sales_funcs.get_special_account(self.special_sale)

        # get COGS
        COGS_amounts = self.COGS()
        for ii in COGS_amounts:
            inv_acct = sales_funcs.get_inventory_account(ii)
            lines.append((inv_acct, -COGS_amounts[ii], self.customer_code, []))
            lines.append((sample_exp_acct, COGS_amounts[ii], self.customer_code, []))
        return lines

    def get_acctrec_lines(self):
        lines = []
        accts_rec = sales_funcs.get_receiveables_account(self.channel.label)
        lines.append((accts_rec, self.total_receivable(), self.payee(), []))
        return lines

    def get_shippingcharge_lines(self):
        lines = []
        if self.shipping_charge > 0:
            shipping_acct = sales_funcs.get_shipping_account()
            lines.append((shipping_acct, - self.shipping_charge, self.customer_code, []))
        return lines

    def get_salestax_lines(self):
        lines = []
        salestax_acct = sales_funcs.get_salestax_account()
        tax_amts = self.get_sales_taxes()
        for entity in tax_amts:
            lines.append((salestax_acct, -tax_amts[entity], entity, []))
        return lines

    def get_giftwrap_lines(self):
        lines = []
        giftwrap_acct = sales_funcs.get_giftwrap_account()
        if self.gift_wrapping:
            lines.append((giftwrap_acct, -self.gift_wrap_fee, self.customer_code, []))
        return lines

    def get_discount_lines(self):
        lines = []
        discount_acct = sales_funcs.get_discount_account(self.channel.label)
        if self.discount and self.discount > 0:
            lines.append((discount_acct, Decimal(self.discount), self.customer_code, []))
        return lines

    def get_channelfee_lines(self):
        lines = []
        channel_id = self.channel.counterparty.id
        if self.channel_charges > 0:
            channelfees_acct = sales_funcs.get_channelfees_account(channel_id)
            lines.append((channelfees_acct,
                          Decimal(self.channel_charges),
                          channel_id, []))
        return lines


    def COGS(self):
        all_items = list(itertools.chain.from_iterable(u.COGS() for u in self.unit_sale.all()))
        key_func = lambda x: x['label']
        gps = itertools.groupby(sorted(all_items, key=key_func), key=key_func)
        return dict((k, sum(a['COGS'] for a in v)) for k, v in gps)


    def get_COGS_lines(self, tag_filter=None):
        lines = []
        COGS_amounts = self.COGS()
        channel_id = self.channel.counterparty.id

        for ii in COGS_amounts:
            inv_acct = sales_funcs.get_inventory_account(ii)
            COGS_acct = sales_funcs.get_COGS_account(ii, channel_id)
            lines.append((inv_acct, -COGS_amounts[ii], self.customer_code, []))
            lines.append((COGS_acct, COGS_amounts[ii], self.customer_code, []))
        return lines


    def get_grosssales_lines(self, tag_filter=None):
        lines = []
        channel_id = self.channel.label
        customer_code = self.customer_code
        
        if not tag_filter:
            unit_sales = self.unit_sale.all()
        elif tag_filter == 'original':
            unit_sales = self.unit_sale.filter(tag__isnull=True)
        else:
            unit_sales = self.unit_sale.filter(tag=tag_filter)

        for u_sale in unit_sales:
            inv_items = u_sale.get_gross_sales()
            for ii in inv_items:
                gross_sales_acct = sales_funcs.get_grosssales_account(ii, channel_id)
                lines.append((gross_sales_acct, -inv_items[ii], customer_code, []))
        return lines


    def get_adjustments(self, date):
        return self.proceedsadjustment_sale.filter(date=self.sale_date)


    def get_gl_transactions(self):
        base_tran = dict(company=self.company,
                         date=self.sale_date,
                         bmo_id='%s.%s' % (self.short_code, self.id),
                         lines=[]
                       )

        if self.special_sale == 'payment':
            tran = dict((k, v) for k, v in base_tran.iteritems())
            tran['comment'] = "Payment - %s: %s" % (self.channel, self.external_channel_id)
            tran['trans_id']='%s.%s.%s' % (self.short_code, self.id, 'SALE')
            tran['lines'] += self.get_payment_lines()
            return [tran]
        elif self.special_sale:
            tran = dict((k, v) for k, v in base_tran.iteritems())
            tran['comment'] = "%s - %s: %s" % (self.special_sale, self.channel, self.external_channel_id)
            tran['trans_id'] ='%s.%s.%s' % (self.short_code, self.id, 'SALE')
            tran['lines'] += self.get_specialsale_lines()
            return [tran]
        else:
            # 1 get original sale
            orig_tran = dict((k, v) for k, v in base_tran.iteritems())
            orig_tran['comment'] = "%s: %s" % (self.channel, self.external_channel_id),
            orig_tran['trans_id'] = '%s.%s.%s' % (self.short_code, self.id, 'SALE'),
                         
            orig_tran['lines'] += self.get_grosssales_lines(tag_filter='original')
            orig_tran['lines'] += self.get_COGS_lines(tag_filter='original')

            
            tran['lines'] += self.get_acctrec_lines()
            tran['lines'] += self.get_shippingcharge_lines()
            tran['lines'] += self.get_salestax_lines()
            tran['lines'] += self.get_giftwrap_lines()
            tran['lines'] += self.get_discount_lines()
            
            tran['lines'] += self.get_channelfee_lines()
            
            # 2 get subsequent adjustments, grouped by date

            
        return [tran]