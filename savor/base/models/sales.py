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
    sale_date = models.DateField()
    external_ref = models.CharField(max_length=50, null=True)

    subtotal = models.DecimalField(max_digits=11, decimal_places=2)
    shipping = models.DecimalField(max_digits=11, decimal_places=2)
    
    discount = models.DecimalField(max_digits=11, decimal_places=2, blank=True, null=True)
    discount_code = models.CharField(max_length=50, blank=True, null=True)

    channel = models.CharField(choices=CHANNELS, max_length=25)
    customer_code = models.CharField(max_length=100)

    memo = models.CharField(max_length=200, null=True)
    fulfill_status = models.CharField(choices=FULFILL_STATUS, max_length=25)
    
    history = HistoricalRecords()


    class Meta:
        app_label = 'base'
        db_table = 'base_sale'

    
    def save(self):
        models.Model.save(self)
        #self.update_gl()

