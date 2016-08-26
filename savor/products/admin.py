from django.contrib import admin
import django.dispatch
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect


from .models import *
from accountifie.common.api import api_func


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
