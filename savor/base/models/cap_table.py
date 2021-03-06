from django.db import models



SHARE_CLASSES = [
    ['common', "Common Stock"],
    ['series_A1', "Series A-1 Preferreds"],
]

class StockEntry(models.Model):
    date = models.DateField()
    quantity = models.IntegerField()
    share_class = models.CharField(choices=SHARE_CLASSES, max_length=20)
    gl_acct = models.ForeignKey('gl.Account')

    class Meta:
        app_label = 'base'
        db_table ='base_stockentry'
