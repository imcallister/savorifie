
from django.db import models


class TaxCollector(models.Model):
    entity = models.CharField(max_length=100)

    def __unicode__(self):
        return self.entity

    class Meta:
        app_label = 'sales'
        db_table = 'sales_taxcollector'


class SalesTax(models.Model):
    sale = models.ForeignKey('sales.Sale', related_name='sales_tax')
    date = models.DateField()
    collector = models.ForeignKey(TaxCollector)
    tax = models.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        app_label = 'sales'
        db_table = 'sales_salestax'

    def __unicode__(self):
        return '%s: %s' % (self.sale, self.collector)
