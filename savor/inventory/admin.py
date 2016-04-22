from django.contrib import admin
import django.dispatch

from .models import *
from accountifie.gl.bmo import on_bmo_save


class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('description', 'short_code',)
    search_fields = ('short_code', 'description',)

admin.site.register(Warehouse, WarehouseAdmin)   


class ProductLineAdmin(admin.ModelAdmin):
    list_display = ('description', 'short_code',)
    search_fields = ('short_code', 'description',)

admin.site.register(ProductLine, ProductLineAdmin)   


class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'short_code', 'product_line',)
    list_filter = ('product_line', )
    search_fields = ('short_code', 'description', 'product_line',)

admin.site.register(InventoryItem, InventoryItemAdmin)   


class SKUUnitInline(admin.TabularInline):
    model = SKUUnit
    can_delete = True
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('description', 'short_code',)
    search_fields = ('short_code', 'description',)

    inlines = [SKUUnitInline]

admin.site.register(Product, ProductAdmin)   


#special signal as normal GL update doesn't work with Shipments
shipment_saved = django.dispatch.Signal(providing_args=[])
shipment_saved.connect(on_bmo_save)


class ShipmentLineInline(admin.TabularInline):
    model = ShipmentLine
    can_delete = True
    extra = 0


class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('description', 'short_code',)
    search_fields = ('short_code', 'description',)

    inlines = [ShipmentLineInline]

    def response_change(self, request, new_object):
        "They saved a change - send signal"
        shipment_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new shipment - send signal"
        shipment_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)

admin.site.register(Shipment, ShipmentAdmin)   


#special signal as normal GL update doesn't work with Transfers
transfer_saved = django.dispatch.Signal(providing_args=[])
transfer_saved.connect(on_bmo_save)


class TransferLineInline(admin.TabularInline):
    model = TransferLine
    can_delete = True
    extra = 0


class InventoryTransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_date', 'location', 'destination',)
    inlines = [TransferLineInline]

    def response_change(self, request, new_object):
        "They saved a change - send signal"
        transfer_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new transfer - send signal"
        transfer_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)

admin.site.register(InventoryTransfer, InventoryTransferAdmin)


#special signal as normal GL update doesn't work with Transfers
#fulfill_saved = django.dispatch.Signal(providing_args=[])
#fulfill_saved.connect(on_bmo_save)


class FulfillLineInline(admin.TabularInline):
    model = FulfillLine
    can_delete = True
    extra = 0


class FulfillUpdateInline(admin.TabularInline):
    model = FulfillUpdate
    can_delete = True
    extra = 0


class FulfillmentAdmin(admin.ModelAdmin):
    list_display = ('request_date', 'warehouse', 'order',)
    inlines = [FulfillLineInline, FulfillUpdateInline]

    def response_change(self, request, new_object):
        "They saved a change - send signal"
        fulfill_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new transfer - send signal"
        fulfill_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)

admin.site.register(Fulfillment, FulfillmentAdmin)


