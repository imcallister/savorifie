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
    list_display = ('channel', 'label', 'ship_type', 'bill_to', 'ship_from',)
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

