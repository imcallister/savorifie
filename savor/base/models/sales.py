from django.utils.safestring import mark_safe
from decimal import Decimal
from django.db import models

from simple_history.models import HistoricalRecords

import accountifie.gl.bmo

DZERO = Decimal('0')

class Product(models.Model):
    description = models.CharField(max_length=50)
    short_code = models.CharField(max_length=20)

    def __unicode__(self):
        return self.short_code

    class Meta:
        app_label = 'base'
        db_table = 'base_product'


class TaxCollector(models.Model):
    entity = models.CharField(max_length=100)

    def __unicode__(self):
        return self.entity

    class Meta:
        app_label = 'base'
        db_table = 'base_taxcollector'


FULFILL_STATUS = [
    ['unfulfilled', "Unfulfilled"],
    ['fulfilled', "Fulfilled"],
]

CHANNELS = [
    ['shopify', "Shopify"],
]

class UnitSale(models.Model):
    sale = models.ForeignKey('base.Sale')
    product = models.ForeignKey('base.Product')
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(default=0, max_digits=11, decimal_places=2)
    
    class Meta:
        app_label = 'base'
        db_table = 'base_unitsale'

    def __unicode__(self):
        return '%s: %s' % (self.sale, self.product)

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
    company = models.ForeignKey('gl.Company', default=accountifie._utils.get_default_company)

    sale_date = models.DateField()
    external_ref = models.CharField(max_length=50, null=True)
    shipping = models.DecimalField(max_digits=11, decimal_places=2)
    discount = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    discount_code = models.CharField(max_length=50, blank=True, null=True)

    channel = models.CharField(choices=CHANNELS, max_length=25)
    customer_code = models.CharField(max_length=100)
    memo = models.CharField(max_length=200, null=True)
    fulfill_status = models.CharField(choices=FULFILL_STATUS, max_length=25)
    
    history = HistoricalRecords()
    short_code = 'SALE'

    class Meta:
        app_label = 'base'
        db_table = 'base_sale'

    def save(self):
        models.Model.save(self)
        self.update_gl()
        
    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)

    @property
    def id_link(self):
        return mark_safe('<a href="/admin/base/sale/%s">%s</a>' % (self.id, self.id))


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
        products = list(set([x.product.short_code for x in unit_sales]))
        sale_amts = dict((p,0) for p in products)
        for s in unit_sales:
            sale_amts[s.product.short_code] += s.quantity * s.unit_price
        
        # apply discount
        if self.discount > 0:
            total_sale = sum([v for k,v in sale_amts.iteritems()])
            for p in products:
                sale_amts[p] -= self.discount * sale_amts[p] / total_sale

        # now get sales_taxes
        sales_taxes = self.salestax_set.all()
        tax_collectors = list(set([t.collector.entity for t in sales_taxes]))
        tax_amts = dict((p,0) for p in tax_collectors)
        for t in sales_taxes:
            tax_amts[t.collector.entity] += t.tax
        
        # calculate total cash = shipping + discount + sum over product x qty + sum of taxes
        total_amount = self.shipping + sum([v for k,v in sale_amts.iteritems()]) + sum([v for k,v in tax_amts.iteritems()])

        # while pre-sale
        # ---------------
        # + total cash to AR
        # each line of taxes goes to sales tax liability account
        # - shipping goes to shipping liability account  (will this always be the same or do we need to capture shippers?)
        # - rest goes to a pre-sale

        tran = []

        accts_rec = accountifie.environment.api.variable({'name': 'GL_ACCOUNTS_RECEIVABLE'})
        
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
        shipping_acct = accountifie.gl.api.account({'path': 'liabilities.curr.accrued.shipping'})['id']
        tran['lines'].append((shipping_acct, -self.shipping, 'retail_buyer', []))

        # TAXES
        sales_tax_acct = accountifie.gl.api.account({'path': 'liabilities.curr.accrued.salestax'})['id']
        for entity in tax_amts:
            tran['lines'].append((sales_tax_acct, -tax_amts[entity], entity, []))

        # book to pre-sales
        for product in sale_amts:
            presale_acct = accountifie.gl.api.account({'path': 'liabilities.curr.presold.%s' % product})['id']
            tran['lines'].append((presale_acct, -sale_amts[product], 'retail_buyer', []))

        return [tran]
