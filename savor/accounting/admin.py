from django.contrib import admin

from .models import *


class COGSAssignmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_line', 'quantity', 'unit_sale',)

admin.site.register(COGSAssignment, COGSAssignmentAdmin)
