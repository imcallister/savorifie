"Re-saves all things which might produce GL transactions."
from optparse import make_option

from django.core.management.base import BaseCommand

from base.models import Sale

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--all',
                    action='store_true', 
                    help='Fill in COGS Assignments'),
        )

    def handle(self, *args, **options):
        qs = Sale.objects.all()
        for obj in qs:
            obj.save()
