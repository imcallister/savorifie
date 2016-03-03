import pytz
import json
import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


from simple_history.models import HistoricalRecords

from accountifie.gl.bmo import BusinessModelObject
import accountifie._utils


EASTERN = pytz.timezone('US/Eastern')

def get_changed(dt):
    cutoff = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=EASTERN)
    qs_list = [nom.history.get_queryset()[0] for nom in NominalTransaction.objects.all()]
    history = [nom.__dict__ for nom in qs_list if nom.history_user_id and nom.history_date > cutoff]

    cols = ['comment', 'history_type', 'date_end', 'company_id', 'object_id', 'history_user_id', 'date', 'history_id', 'id', 'history_date']

    filt_history = [dict((k,str(v)) for k,v in nom.iteritems() if k in cols) for nom in history]
    return json.dumps(filt_history)



class NominalTranLine(models.Model):
    transaction = models.ForeignKey('base.NominalTransaction')
    account = models.ForeignKey('gl.Account')
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    counterparty = models.ForeignKey('gl.Counterparty')

    class Meta:
        app_label = 'base'
        db_table ='base_nominaltranline'


class NominalTransaction(models.Model, BusinessModelObject):
    """Allows manual entry of double-entry transactions.
    
    Supports two or more line items.
    This is also an example of a BusinessModelObject - something
    that creates an entry in the General Ledger.  We import from
    the legacy data into these.
    
    """
    company = models.ForeignKey('gl.Company', default=accountifie._utils.get_default_company)
    date = models.DateField(db_index=True)
    date_end = models.DateField(db_index=True, blank=True, null=True)

    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    source_object =  GenericForeignKey()

    comment = models.CharField(max_length=200, default="None")

    history = HistoricalRecords()
    short_code = 'NOML'

    class Meta:
        app_label = 'base'
        db_table = 'base_nominaltransaction'

    def __unicode__(self):
        return u"%s: %s" % (self.id, self.date)

    
    def save(self):
        models.Model.save(self)

        self.update_gl()
        
    def delete(self):
        self.delete_from_gl()
        models.Model.delete(self)

    @property
    def account0(self):
        tranlines = self.nominaltranline_set.all()
        return str(tranlines[0].account)

    @property
    def account1(self):
        tranlines = self.nominaltranline_set.all()
        return str(tranlines[1].account)

    @property
    def amount0(self):
        tranlines = self.nominaltranline_set.all()
        return "{:,.0f}".format(tranlines[0].amount)

    @property
    def amount1(self):
        tranlines = self.nominaltranline_set.all()
        return "{:,.0f}".format(tranlines[1].amount)


    def get_gl_transactions(self):
        "Creates entries for general ledger"        

        lines = []
        for line in self.nominaltranline_set.all():
            lines.append((line.account, line.amount, line.counterparty, []))
        
        # if linked to another object use that in ID
        if self.object_id is not None:
            cmpnt3 = '%s_%s' % (self.content_type.name, self.object_id)
        else:
            cmpnt3 = 'GEN'

        trans = dict(
            company=self.company,
            date=self.date,
            date_end=self.date_end,
            comment=self.comment,
            trans_id='%s.%s.%s' % (self.short_code, self.id, cmpnt3),
            bmo_id=self.id,
            lines=lines
            )
        return [trans]
