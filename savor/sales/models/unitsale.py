import itertools
from decimal import Decimal
import datetime

from django.db import models

from accounting.serializers import COGSAssignmentSerializer



UNITSALE_TAGS = (
    ('RETURN', 'Return'),
    ('REPLACEMENT', 'Replacement'),
    ('PAYMENT', 'Payment'),
)

class UnitSale(models.Model):
    sale = models.ForeignKey('sales.Sale', related_name='unit_sale')
    date = models.DateField()
    sku = models.ForeignKey('products.Product')
    quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(default=0, max_digits=11, decimal_places=2)
    tag = models.CharField(max_length=20, choices=UNITSALE_TAGS, blank=True, null=True)

    class Meta:
        app_label = 'sales'
        db_table = 'sales_unitsale'

    def __unicode__(self):
        return '%s - %s:%s' % (self.id, self.sale, self.sku)

    def default_date(self):
        try:
            return self.sale.sale_date
        except:
            return datetime.date(2016,1,1)

    def save(self):
        models.Model.save(self)
        self.assignCOGS()

    def assignCOGS(self):
        import accounting.jobs
        accounting.jobs.fifo_assign(self.id, self.unassigned_COGS())


    def unassigned_COGS(self):
        qs = self.cogsassignment_set.all()
        assignments = COGSAssignmentSerializer(qs, many=True).data
        key_func = lambda x: x['unit_label']
        gps = itertools.groupby(sorted(assignments, key=key_func), key=key_func)
        
        assigned = dict((k, sum(e['quantity'] for e in list(g))) for k, g in gps)
        items = self.inventory_items()

        unassigned = dict((k, items.get(k, 0) - assigned.get(k, 0)) for k in list(set(assigned.keys() + items.keys())))
        return dict((k, v) for k, v in unassigned.iteritems() if v != 0)

        
    def COGS(self):
        qs = self.cogsassignment_set.all()
        assignments = COGSAssignmentSerializer(qs, many=True).data
        key_func = lambda x: x['unit_label']
        gps = itertools.groupby(sorted(assignments, key=key_func), key=key_func)
        return [{'label': k, 'COGS': sum(a['quantity'] * a['cost'] for a in v)} for k, v in gps]


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

