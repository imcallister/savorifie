from django.contrib import admin

from .models import *



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


class SKUAdmin(admin.ModelAdmin):
    list_display = ('description', 'short_code',)
    search_fields = ('short_code', 'description',)

    inlines = [SKUUnitInline]

admin.site.register(SKU, SKUAdmin)   
