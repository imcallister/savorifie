from django.db import models


from simple_history.models import HistoricalRecords

import accountifie.gl.models
from accountifie.gl.bmo import BusinessModelObject
from accountifie.toolkit.utils import get_default_company
from accountifie.common.api import api_func


class CreditCardTrans(models.Model, BusinessModelObject):
    company = models.ForeignKey('gl.Company', default=get_default_company)
    card_company = models.ForeignKey('gl.Counterparty', related_name='card_company')
    counterparty = models.ForeignKey('gl.Counterparty', related_name='counterparty')

    trans_date = models.DateField()
    post_date = models.DateField()
    trans_type = models.CharField(max_length=20, null=True)
    trans_id = models.CharField(max_length=50, null=True)

    amount = models.FloatField(null=True)
    description = models.TextField(max_length=200, null=True, blank=True)
    payee = models.CharField(max_length=200, null=True, blank=True)
    card_number = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return '%s:%s' % (str(self.card_company), self.trans_id)

    class Meta:
        app_label = 'base'
        verbose_name = "Credit Card Transaction"
        verbose_name_plural = "Credit Card Transactions"
        db_table = 'base_creditcardtransactions'

    history = HistoricalRecords()
    short_code = 'CCARD'
