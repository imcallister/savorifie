from django.utils.safestring import mark_safe
from decimal import Decimal
from django.db import models

from simple_history.models import HistoricalRecords

import accountifie.gl.bmo
from accountifie.toolkit.utils import get_default_company
from accountifie.common.api import api_func

DZERO = Decimal('0')


class TaxCollector(models.Model):
    entity = models.CharField(max_length=100)

    def __unicode__(self):
        return self.entity

    class Meta:
        app_label = 'base'
        db_table = 'base_taxcollector'


class Channel(models.Model):
    counterparty = models.ForeignKey('gl.Counterparty')

    def __unicode__(self):
        return self.counterparty.name

CHANNELS = [
    ['shopify', "Shopify"],
]


class UnitSale(models.Model):
    sale = models.ForeignKey('base.Sale')
    sku = models.ForeignKey('inventory.Product', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(default=0, max_digits=11, decimal_places=2)

    class Meta:
        app_label = 'base'
        db_table = 'base_unitsale'

    def __unicode__(self):
        return '%s: %s' % (self.sale, self.sku)

    def get_inventory_items(self):
        return dict((u.inventory_item.label, u.quantity * self.quantity) for u in self.sku.skuunit_set.all())

    @property
    def items_string(self):
        return ','.join(['%s %s' % (u.quantity * self.quantity, u.inventory_item.label) for u in self.sku.skuunit_set.all()])


class SalesTax(models.Model):
    sale = models.ForeignKey('base.Sale')
    collector = models.ForeignKey('base.TaxCollector')
    tax = models.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        app_label = 'base'
        db_table = 'base_salestax'

    def __unicode__(self):
        return '%s: %s' % (self.sale, self.collector)


class Sale(models.Model, accountifie.gl.bmo.BusinessModelObject):
    company = models.ForeignKey('gl.Company', default=get_default_company)

    channel = models.ForeignKey(Channel, blank=True, null=True)
    sale_date = models.DateField()
    external_channel_id = models.CharField(max_length=50, blank=True, null=True)
    external_ref = models.CharField(max_length=50, blank=True, null=True)
    external_routing_id = models.CharField(max_length=50, blank=True, null=True)

    shipping_code = models.CharField(max_length=50, blank=True, null=True)
    shipping_charge = models.DecimalField(max_digits=11, decimal_places=2)

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
        if self.external_channel_id:
            sale_id = self.external_channel_id
        elif self.external_ref:
            sale_id = self.external_ref
        else:
            sale_id = self.id

        return '%s: %s' % (self.channel.counterparty.id, sale_id)

    class Meta:
        app_label = 'base'
        db_table = 'base_sale'

    def save(self):
        self.update_gl()
        models.Model.save(self)
        
    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)

    @property
    def fulfill_requested(self):
        fulfillment_labels = [x['order'] for x in api_func('inventory', 'fulfillment')]
        order_label = api_func('base', 'sale', unicode(order_id))['label']

        if order_label in fulfillment_labels:
            return True
        else:
            return False


    @property
    def id_link(self):
        return mark_safe('<a href="/admin/base/sale/%s">%s</a>' % (self.id, self.id))

    @property
    def channel_name(self):
        return str(self.channel)

    @property
    def items_string(self):
        return ','.join([u.items_string for u in self.unitsale_set.all()])


    @property
    def label(self):
        return str(self)


    def _get_unitsales(self):
        unitsales = self.unitsale_set.all()

        unitsale_lines = []
        for unit in unitsales:
            unit

        running_total = DZERO
        if len(allocations) > 0:
            for allocation in allocations:
                if allocation.project is None:
                    tags = []
                else:
                    tags = ['project_%s' % allocation.project.id]

                alloc_lines.append((allocation.trans_type, DZERO - Decimal(allocation.amount), allocation.counterparty, tags))
                running_total += Decimal(allocation.amount)

        if abs(Decimal(self.amount) - running_total) >= Decimal('0.005'):
            alloc_lines.append((self.ext_account.gl_account, DZERO - (Decimal(self.amount) - running_total), None, []))

        return alloc_lines

    def _get_salestaxes(self):
        allocations = self.salestax_set.all()

        alloc_lines = []
        running_total = DZERO
        if len(allocations) > 0:
            for allocation in allocations:
                if allocation.project is None:
                    tags = []
                else:
                    tags = ['project_%s' % allocation.project.id]

                alloc_lines.append((allocation.trans_type, DZERO - Decimal(allocation.amount), allocation.counterparty, tags))
                running_total += Decimal(allocation.amount)

        if abs(Decimal(self.amount) - running_total) >= Decimal('0.005'):
            alloc_lines.append((self.ext_account.gl_account, DZERO - (Decimal(self.amount) - running_total), None, []))

        return alloc_lines


    def get_gl_transactions(self):

        # for starters implement only for pre-sale

        unit_sales = self.unitsale_set.all()
        skus = list(set([x.sku for x in unit_sales]))

        sale_amts = dict((s,0) for s in skus)
        for s in unit_sales:
            sale_amts[s.sku] += Decimal(s.quantity) * Decimal(s.unit_price)

        # apply discount
        if self.discount > 0:
            total_sale = sum([v for k,v in sale_amts.iteritems()])
            for s in skus:
                sale_amts[s] -= Decimal(self.discount) * Decimal(sale_amts[s]) / Decimal(total_sale)

        # now get sales_taxes
        sales_taxes = self.salestax_set.all()
        tax_collectors = list(set([t.collector.entity for t in sales_taxes]))
        tax_amts = dict((p,0) for p in tax_collectors)
        for t in sales_taxes:
            tax_amts[t.collector.entity] += Decimal(t.tax)

        # calculate total cash = shipping + discount + sum over product x qty + sum of taxes
        total_amount = Decimal(self.shipping_charge) + sum([v for k,v in sale_amts.iteritems()]) + sum([v for k,v in tax_amts.iteritems()]) + Decimal(self.gift_wrap_fee)

        # while pre-sale
        # ---------------
        # + total cash to AR
        # each line of taxes goes to sales tax liability account
        # - shipping goes to shipping liability account  (will this always be the same or do we need to capture shippers?)
        # - rest goes to a pre-sale

        tran = []

        accts_rec = api_func('environment', 'variable', 'GL_ACCOUNTS_RECEIVABLE')
        
        tran = dict(company=self.company,
                    date=self.sale_date,
                    comment= "%s: %s" % (self.channel, self.external_ref),
                    trans_id='%s.%s.%s' % (self.short_code, self.id, 'SALE'),
                    bmo_id='%s.%s' % (self.short_code, self.id),
                    lines=[]
                    )

        # ACCOUNTS RECEIVABLE
        tran['lines'].append((accts_rec, total_amount, 'retail_buyer', []))

        # SHIPPING
        shipping_acct = api_func('gl', 'account', 'liabilities.curr.accrued.shipping')['id']
        tran['lines'].append((shipping_acct, - self.shipping_charge, 'retail_buyer', []))

        # GIFT-WRAPPING
        giftwrap_acct = api_func('gl', 'account', 'equity.retearnings.sales.extra.giftwrap')['id']
        tran['lines'].append((giftwrap_acct, -self.gift_wrap_fee, 'retail_buyer', []))

        # TAXES
        sales_tax_acct = api_func('gl', 'account', 'liabilities.curr.accrued.salestax')['id']
        for entity in tax_amts:
            tran['lines'].append((sales_tax_acct, -tax_amts[entity], entity, []))

        # book to pre-sales
        for sku in sale_amts:
            # now loop through the sku unit in the sku
            sku_items = sku.skuunit_set.all()
            for sku_item in sku_items:
                product_line = sku_item.inventory_item.product_line.label
                rev_percent = Decimal(sku_item.rev_percent)/Decimal(100)
                presale_acct = api_func('gl', 'account', 'liabilities.curr.presold.%s' % product_line)['id']
                tran['lines'].append((presale_acct, -sale_amts[sku] * rev_percent, 'retail_buyer', []))

        return [tran]
