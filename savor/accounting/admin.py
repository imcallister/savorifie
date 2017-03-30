from django.contrib import admin

from .models import *


class COGSAssignmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_line', 'quantity', 'unit_sale',)
    list_select_related = ('unit_sale__sale__channel__counterparty', 'channel',)

    def formfield_for_foreignkey(self, db_field, request=None,**kwargs):
        field = super(COGSAssignmentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'unit_sale':
            field.queryset = field.queryset.select_related('sale__channel__counterparty', 'sku')
        elif db_field.name == 'shipment_line':
            field.queryset = field.queryset.select_related('inventory_item', 'shipment')
        return field

admin.site.register(COGSAssignment, COGSAssignmentAdmin)
