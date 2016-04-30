from django.contrib import admin
import django.dispatch

from .models import *
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

    """
    def response_change(self, request, new_object):
        "They saved a change - send signal"
        fulfill_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new transfer - send signal"
        fulfill_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)
    """

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

    """
    def response_change(self, request, new_object):
        "They saved a change - send signal"
        fulfill_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new transfer - send signal"
        fulfill_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)
    """

admin.site.register(InventoryTransfer, InventoryTransferAdmin)



class WarehouseFulfillLineInline(admin.TabularInline):
    model = WarehouseFulfillLine
    can_delete = True
    extra = 0



class WarehouseFulfillAdmin(admin.ModelAdmin):
    list_display = ('savor_order', 'savor_transfer', 'warehouse', 'warehouse_pack_id', 'ship_date', 'shipping_code', 'tracking_number',)
    inlines = [WarehouseFulfillLineInline,]

    """
    def response_change(self, request, new_object):
        "They saved a change - send signal"
        fulfill_saved.send(new_object)
        return admin.ModelAdmin.response_change(self, request, new_object)

    def response_add(self, request, obj):
        "They added a new transfer - send signal"
        fulfill_saved.send(obj)
        return admin.ModelAdmin.response_add(self, request, obj)
    """

admin.site.register(WarehouseFulfill, WarehouseFulfillAdmin)
