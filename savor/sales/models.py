from django.utils.safestring import mark_safe
from decimal import Decimal
import logging
import itertools

from django.db import models

from simple_history.models import HistoricalRecords

import accountifie.gl.bmo
from accountifie.toolkit.utils import get_default_company
from accountifie.common.api import api_func
import accounting.models
from accountifie.gl.models import Account, Counterparty


DZERO = Decimal('0')

logger = logging.getLogger('default')


class Channel(models.Model):
    label = models.CharField(max_length=20)
    counterparty = models.ForeignKey(Counterparty)

    class Meta:
        app_label = 'sales'
        db_table = 'base_channel'

    def __unicode__(self):
        return self.label

CHANNELS = [
    ['shopify', "Shopify"],
]


class TaxCollector(models.Model):
    entity = models.CharField(max_length=100)

    def __unicode__(self):
        return self.entity

    class Meta:
        app_label = 'sales'
        db_table = 'base_taxcollector'


class UnitSale(models.Model):
    sale = models.ForeignKey('sales.Sale', related_name='unit_sale')
    sku = models.ForeignKey('products.Product', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(default=0, max_digits=11, decimal_places=2)

    class Meta:
        app_label = 'sales'
        db_table = 'base_unitsale'

    def __unicode__(self):
        return '%s - %s:%s' % (self.id, self.sale, self.sku)

    def save(self, update_gl=True):
        models.Model.save(self)
        
        if update_gl:
            # need to do FIFO assignment
            to_be_fifod = self.fifo_check()
            if len(to_be_fifod) > 0:
                accounting.models.fifo_assign(self.id, to_be_fifod)


    def fifo_check(self):
        if self.id:
            fifos = api_func('accounting', 'fifo_assignment', self.id)
        else:
            fifos = []

        # tally the count by SKU
        # (there may be SKUs assigned to different shipments etc)
        fifo_skus = list(set([x['sku'] for x in fifos]))
        fifo_sku_count = dict((s, 0) for s in fifo_skus)

        for fifo in fifos:
            fifo_sku_count[fifo['sku']] += fifo['quantity']

        sku_items = self.inventory_items()
        diff = dict((s, sku_items.get(s, 0) - fifo_sku_count.get(s, 0)) for s in sku_items)
        diff = dict((k,v) for k,v in diff.iteritems() if v>0)
        return diff

    def inventory_items(self):
        return dict((u.inventory_item.label, u.quantity * self.quantity) for u in self.sku.skuunit.all())

    def get_inventory_items(self):
        return dict((u.inventory_item.label, u.quantity * self.quantity) for u in self.sku.skuunit.all())

    def get_gross_sales(self):
        return dict((u.inventory_item.label,
                     u.quantity * self.quantity * self.unit_price * Decimal(u.rev_percent)/Decimal(100)) \
                    for u in self.sku.skuunit.all())

    @property
    def items_string(self):
        items = [(u.quantity * self.quantity, u.inventory_item.label) for u in self.sku.skuunit.all()]
        items = sorted(items, key=lambda x: x[1])
        return ','.join(['%s %s' % (i[0], i[1]) for i in items])




SPECIAL_SALES = (
    ('press', 'Press Sample'),
    ('consignment', 'Consignment'),
    ('prize', 'Gift/Prize'),
    ('retailer', 'Retailer Sample'),
)

class Sale(models.Model, accountifie.gl.bmo.BusinessModelObject):
    company = models.ForeignKey('gl.Company', default=get_default_company)

    channel = models.ForeignKey(Channel, blank=True, null=True)
    sale_date = models.DateField()
    external_channel_id = models.CharField(max_length=50, unique=True,
                                           blank=True, null=True,
                                           help_text='If no ID, leave blank for system-generated ID')
    external_routing_id = models.CharField(max_length=50, blank=True, null=True)
    special_sale = models.CharField(max_length=20, choices=SPECIAL_SALES, blank=True, null=True)
    ship_type = models.ForeignKey('inventory.ChannelShipmentType', blank=True, null=True, default=None)

    shipping_charge = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal(0))

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
        else:
            sale_id = 'SAV.' + str(self.id)

        return '%s: %s' % (self.channel.counterparty.id, sale_id)

    class Meta:
        app_label = 'sales'
        db_table = 'base_sale'

    def save(self, update_gl=True):
        if not self.external_channel_id:
            if self.special_sale:
                sample_ids = [s['external_channel_id'].lower() for s in Sale.objects \
                                                     .filter(external_channel_id__icontains='sample') \
                                                     .values('external_channel_id')]
                special_ids = [s['external_channel_id'].lower() for s in Sale.objects \
                                                      .filter(external_channel_id__icontains='special') \
                                                      .values('external_channel_id')]

                sample_ids = [int(s.replace('sample', '')) for s in sample_ids]
                special_ids = [int(s.replace('special', '')) for s in special_ids]
                used_ids = sample_ids + special_ids
                if len(used_ids) == 0:
                    max_id = 0
                else:
                    max_id = max(used_ids)
                self.external_channel_id = 'SPECIAL%d' % (max_id + 1)
            else:
                ch_lbl = str(self.channel)
                auto_ids = [s['external_channel_id'] for s in Sale.objects \
                                                      .filter(external_channel_id__icontains=ch_lbl) \
                                                      .values('external_channel_id')]
                print auto_ids
                used_ids = [int(s.replace(ch_lbl + '.', '')) for s in auto_ids]
                if len(used_ids) == 0:
                    max_id = 0
                else:
                    max_id = max(used_ids)
                self.external_channel_id = '%s.%d' % (ch_lbl, max_id + 1)
        if update_gl:
            # fifo check
            for u in self.unit_sale.all():
                to_be_fifod = u.fifo_check()
                if len(to_be_fifod) > 0:
                    accounting.models.fifo_assign(u.id, to_be_fifod)

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
        return mark_safe('<a href="/admin/sales/sale/%s">%s</a>' % (self.id, self.id))

    @property
    def channel_name(self):
        return str(self.channel)

    @property
    def items_string(self):
        items = [(k, v) for k, v in self.inventory_items.iteritems()]
        items = sorted(items, key=lambda x: x[0])
        return ','.join(['%s %s' % (i[1], i[0]) for i in items])

    @property
    def unfulfilled_items_string(self):
        unf = self.unfulfilled_items
        if unf:
            items = [(k, v) for k, v in unf.iteritems()]
            items = sorted(items, key=lambda x: x[0])
            return ','.join(['%s %s' % (i[1], i[0]) for i in items])
        else:
            return ''

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
        all_items = list(itertools.chain.from_iterable(items))
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
            unf = {k: int(d1.get(k, 0)) - int(d2.get(k,0)) for k in set(d1) | set(d2) }
            unf = dict((k, v) for k,v in unf.iteritems() if v > 0)
            if len(unf) > 0:
                return unf
            else:
                return None
        else:
            return d1

    @property
    def label(self):
        return str(self)


    def _get_unitsales(self):
        unitsales = self.unit_sale.all()

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


    def gross_sale_proceeds(self):
        return sum([v for k,v in self.__sale_amts.iteritems()])


    def total_sales_tax(self):
        sales_tax = sum([v for k, v in self.__tax_amts.iteritems()])
        if sales_tax:
            return sales_tax
        else:
            return Decimal('0')


    def total_receivable(self):
        total = self.gross_sale_proceeds()
        if self.discount:
            total -= Decimal(self.discount)
        if self.shipping_charge:
            total += Decimal(self.shipping_charge)
        if self.gift_wrap_fee:
            total += Decimal(self.gift_wrap_fee)
        total += self.total_sales_tax()
        return total

    def payee(self):
        if self.channel.label == 'SAV':
            return self.customer_code
        else:
            return self.channel.counterparty


    def _get_special_account(self):
        """
        Get account to book special sale to
        """
        if self.special_sale:
            path = 'equity.retearnings.sales.samples.%s' % self.special_sale
            return Account.objects \
                          .filter(path=path) \
                          .first()
        else:
            return None

    def _get_sales_taxes(self):
        sales_taxes = self.salestax_set.all()
        tax_collectors = list(set([t.collector.entity for t in sales_taxes]))
        self.__tax_amts = dict((p,0) for p in tax_collectors)
        for t in sales_taxes:
            self.__tax_amts[t.collector.entity] += Decimal(t.tax)

    def _get_unit_sales(self):
        self.__unit_sales = self.unit_sale.all()
        skus = list(set([x.sku for x in self.__unit_sales]))
        self.__sale_amts = dict((s,0) for s in skus)
        for s in self.__unit_sales:
            self.__sale_amts[s.sku] += Decimal(s.quantity) * Decimal(s.unit_price)


    def get_gl_transactions(self):

        # collect all the info first
        # TO DO have to make sure about order here
        self._get_unit_sales()
        self._get_sales_taxes()
        channel_id = self.channel.counterparty.id

        tran = dict(company=self.company,
                    date=self.sale_date,
                    comment= "%s: %s" % (self.channel, self.external_channel_id),
                    trans_id='%s.%s.%s' % (self.short_code, self.id, 'SALE'),
                    bmo_id='%s.%s' % (self.short_code, self.id),
                    lines=[]
                    )
        accts_rec = Account.objects.get(id=api_func('environment', 'variable', 'GL_ACCOUNTS_RECEIVABLE'))

        shipping_acct = Account.objects.filter(path='liabilities.curr.accrued.shipping').first()
        giftwrap_acct = Account.objects.filter(path='equity.retearnings.sales.extra.giftwrap').first()
        sales_tax_acct = Account.objects.filter(path='liabilities.curr.accrued.salestax').first()
        discount_acct = Account.objects \
                               .filter(path='equity.retearnings.sales.discounts.%s' \
                                            % channel_id) \
                               .first()

        if self.special_sale:
            sample_exp_acct = self._get_special_account()
            for u_sale in self.__unit_sales:
                inv_items = u_sale.inventory_items()
                for ii in inv_items:
                    product_line = api_func('products', 'inventoryitem', ii)['product_line']['label']
                    inv_acct_path = 'assets.curr.inventory.%s.%s' % (product_line, ii)
                    inv_acct = Account.objects.filter(path=inv_acct_path).first()
                    COGS = accounting.models.total_COGS(u_sale, ii)
                    qty = inv_items[ii]
                    tran['lines'].append((inv_acct, -COGS * qty, self.customer_code, []))
                    tran['lines'].append((sample_exp_acct, COGS * qty, self.customer_code, []))
        else:
            # ACCOUNTS RECEIVABLE
            tran['lines'].append((accts_rec, self.total_receivable(), self.payee(), []))

            # SHIPPING
            if self.shipping_charge > 0:
                tran['lines'].append((shipping_acct, - self.shipping_charge, self.customer_code, []))

            # GIFT-WRAPPING
            if self.gift_wrapping:
                tran['lines'].append((giftwrap_acct, -self.gift_wrap_fee, self.customer_code, []))

            # TAXES
            if self.total_sales_tax() > 0:
                for entity in self.__tax_amts:
                    tran['lines'].append((sales_tax_acct, -self.__tax_amts[entity], entity, []))

            # DISCOUNTS
            if self.discount and self.discount > 0:
                tran['lines'].append((discount_acct, Decimal(self.discount), self.customer_code, []))

            # INVENTORY, GROSS SALES & COGS
            for u_sale in self.__unit_sales:
                inv_items = u_sale.get_gross_sales()
                for ii in inv_items:

                    product_line = api_func('products', 'inventoryitem', ii)['product_line']['label']
                    inv_acct_path = 'assets.curr.inventory.%s.%s' % (product_line, ii)
                    inv_acct = Account.objects.filter(path=inv_acct_path).first()

                    COGS_acct_path = 'equity.retearnings.sales.COGS.%s.%s' % (channel_id, product_line)
                    COGS_acct = Account.objects.filter(path=COGS_acct_path).first()
                    COGS = accounting.models.total_COGS(u_sale, ii)

                    gross_sales_acct_path = 'equity.retearnings.sales.gross.%s.%s' % (channel_id, product_line)
                    gross_sales_acct = Account.objects.filter(path=gross_sales_acct_path).first()

                    tran['lines'].append((inv_acct, -COGS, self.customer_code, []))
                    tran['lines'].append((COGS_acct, COGS, self.customer_code, []))
                    tran['lines'].append((gross_sales_acct, -inv_items[ii], self.customer_code, []))

        return [tran]

class SalesTax(models.Model):
    sale = models.ForeignKey(Sale)
    collector = models.ForeignKey(TaxCollector)
    tax = models.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        app_label = 'sales'
        db_table = 'base_salestax'

    def __unicode__(self):
        return '%s: %s' % (self.sale, self.collector)
