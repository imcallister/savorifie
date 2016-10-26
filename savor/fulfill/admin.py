from django.contrib import admin
import django.dispatch
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect

from .models import *
import fulfill.apiv1 as fulfill_api


class ShippingMissing(SimpleListFilter):
    title = 'shipping_missing'
    parameter_name = 'shipping_missing'

    def lookups(self, request, model_admin):
            return (('complete', 'Shipping Info Complete'), ('incomplete', 'Shipping Info Incomplete'))

    def queryset(self, request, qs):
        if self.value():
            fulfillment_ids = [x['id'] for x in fulfill_api.fulfillment({})
                               if x['ship_info'] == self.value() and x['status'] == 'requested']
            return qs.filter(id__in=fulfillment_ids)


class FulfillLineInline(admin.TabularInline):
    model = FulfillLine
    can_delete = True
    extra = 0


class FulfillUpdateInline(admin.TabularInline):
    model = FulfillUpdate
    can_delete = True
    extra = 0


class FulfillmentAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'request_date', 'status', 'warehouse', 'ship_type', 'bill_to', 'use_pdf', 'packing_type',)
    list_filter = ('warehouse', 'status', ShippingMissing,)
    inlines = [FulfillLineInline, FulfillUpdateInline]

admin.site.register(Fulfillment, FulfillmentAdmin)


class ShippingChargeAdmin(admin.ModelAdmin):
    list_display = ('shipper', 'tracking_number', 'external_id','invoice_number', 'ship_date',
                    'charge', 'fulfillment', 'account', 'order_related')
    list_filter = ('order_related',)
    search_fields = ('external_id', 'tracking_number', 'invoice_number',)
    ordering = ('-ship_date',)
    
admin.site.register(ShippingCharge, ShippingChargeAdmin)


class BatchRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_date', 'location', )
    filter_horizontal = ('fulfillments',)
    
admin.site.register(BatchRequest, BatchRequestAdmin)


class WarehouseFulfillLineInline(admin.TabularInline):
    model = WarehouseFulfillLine
    can_delete = True
    extra = 0



class WarehouseFulfillAdmin(admin.ModelAdmin):
    list_display = ('fulfillment', 'warehouse',
                    'warehouse_pack_id', 'ship_date', 'shipping_type',
                    'tracking_number', 'shipping_zip',)
    list_filter = ('warehouse', )
    inlines = [WarehouseFulfillLineInline,]

admin.site.register(WarehouseFulfill, WarehouseFulfillAdmin)
