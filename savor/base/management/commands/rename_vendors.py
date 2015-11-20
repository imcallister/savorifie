"One-off command for use in June 9th, switching to text codes"
import os, time
from optparse import make_option


from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from base.matching import match_expenses_to_vendors, old_to_new_vendors
from base.models import Expense, Mcard
from accountifie.gl.models import Counterparty

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--all',
                action='store_true', 
                help='Remove all matches and re-do'),
        )
        
    
    def handle(self, *args, **options):
        Expense.objects.all().delete()


        mapping = old_to_new_vendors()

        for cp in Counterparty.objects.all():
            if len(cp.id) == 3 and cp.id[0] == '0':
                new_id = mapping[cp.id]
                if len(new_id) > 12:
                    print 'too long:', new_id
                else:
                    cp.id = new_id
                    cp.save()

        #pass 2
        Counterparty.objects.filter(id__startswith='0').delete()


        