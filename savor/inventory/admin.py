from django.contrib import admin
import django.dispatch
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect


from .models import *
from accountifie.common.api import api_func
#from accountifie.gl.bmo import on_bmo_save


class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('description', 'label',)
    search_fields = ('label', 'description',)

admin.site.register(Warehouse, WarehouseAdmin)   


class ProductLineAdmin(admin.ModelAdmin):
    list_display = ('description', 'label',)
    search_fields = ('label', 'description',)

admin.site.register(ProductLine, ProductLineAdmin)   


class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'label', 'product_line',)
    list_filter = ('product_line', )
    search_fields = ('label', 'description', 'product_line',)

admin.site.register(InventoryItem, InventoryItemAdmin)   


class SKUUnitInline(admin.TabularInline):
    model = SKUUnit
    can_delete = True
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('description', 'label',)
    search_fields = ('label', 'description',)

    inlines = [SKUUnitInline]

admin.site.register(Product, ProductAdmin)   


# special signal as normal GL update doesn't work with Shipments

"""
shipment_saved = django.dispatch.Signal(providing_args=[])
shipment_saved.connect(on_bmo_save)
"""

class ShipperAdmin(admin.ModelAdmin):
    list_display = ('company',)


class ShippingTypeAdmin(admin.ModelAdmin):
    list_display = ('shipper', 'label', 'description',)
    list_filter = ('shipper',)


class ChannelShipmentTypeAdmin(admin.ModelAdmin):
    list_display = ('channel', 'label', 'ship_type', 'bill_to',)
    list_filter = ('channel',)

admin.site.register(Shipper, ShipperAdmin)
admin.site.register(ShippingType, ShippingTypeAdmin)
admin.site.register(ChannelShipmentType, ChannelShipmentTypeAdmin)


class ShipmentLineInline(admin.TabularInline):
    model = ShipmentLine
    can_delete = True
    extra = 0


class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('description', 'label',)
    search_fields = ('label', 'description',)

    inlines = [ShipmentLineInline]

    """
    def response_change(self, request, new_object):
        "They saved a change - send signal"
        shipment_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new shipment - send signal"
        shipment_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)
    """
admin.site.register(Shipment, ShipmentAdmin)



#special signal as normal GL update doesn't work with Transfers
#fulfill_saved = django.dispatch.Signal(providing_args=[])
#fulfill_saved.connect(on_bmo_save)

class ShippingMissing(SimpleListFilter):
    title = 'shipping_missing'
    parameter_name = 'shipping_missing'

    def lookups(self, request, model_admin):
            return (('complete', 'Shipping Info Complete'), ('incomplete', 'Shipping Info Incomplete'))

    def queryset(self, request, qs):
        if self.value():
            fulfillment_ids = [x['id'] for x in api_func('inventory', 'fulfillment')
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


#special signal as normal GL update doesn't work with Transfers
#fulfill_saved = django.dispatch.Signal(providing_args=[])
#fulfill_saved.connect(on_bmo_save)


class TransferLineInline(admin.TabularInline):
    model = TransferLine
    can_delete = True
    extra = 0


class TransferUpdateInline(admin.TabularInline):
    model = TransferUpdate
    can_delete = True
    extra = 0


class InventoryTransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_date', 'location', 'destination',)
    inlines = [TransferLineInline, TransferUpdateInline]

    def response_add(self, request, obj):
        if "next" in request.GET:
            return HttpResponseRedirect(request.GET['next'])
        else:
            return admin.ModelAdmin.response_add(self, request, obj)

admin.site.register(InventoryTransfer, InventoryTransferAdmin)


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
    inlines = [WarehouseFulfillLineInline,]

admin.site.register(WarehouseFulfill, WarehouseFulfillAdmin)
