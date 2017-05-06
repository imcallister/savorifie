from accountifie.common.serializers import EagerLoadingMixin

from ..models import  Sale, SalesTax
from rest_framework import serializers



class SalesTaxSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['sale__channel__counterparty', 'collector']

    sale_date = serializers.SerializerMethodField()
    taxable = serializers.SerializerMethodField()
    sale = serializers.StringRelatedField()
    collector = serializers.StringRelatedField()

    def get_sale_date(self, obj):
        return obj.sale.sale_date

    def get_taxable(self, obj):
        return obj.sale.taxable_proceeds()

    class Meta:
        model = SalesTax
        fields = ('sale_date', 'sale', 'collector', 'taxable', 'tax',)


class SalesTaxSerializer2(serializers.ModelSerializer, EagerLoadingMixin):

    taxable = serializers.SerializerMethodField()
    salestax1 = serializers.SerializerMethodField()
    salestax2 = serializers.SerializerMethodField()
    collector1 = serializers.SerializerMethodField()
    collector2 = serializers.SerializerMethodField()

    def get_taxable(self, obj):
        return obj.taxable_proceeds()

    def get_collector1(self, obj):
        sales_taxes = obj.sales_tax.all()
        if len(sales_taxes) > 0:
            return str(sales_taxes[0].collector)
        else:
            return ''

    def get_salestax1(self, obj):
        sales_taxes = obj.sales_tax.all()
        if len(sales_taxes) > 0:
            return sales_taxes[0].tax
        else:
            return 0

    def get_collector2(self, obj):
        sales_taxes = obj.sales_tax.all()
        if len(sales_taxes) > 1:
            return str(sales_taxes[1].collector)
        else:
            return ''

    def get_salestax2(self, obj):
        sales_taxes = obj.sales_tax.all()
        if len(sales_taxes) > 1:
            return sales_taxes[1].tax
        else:
            return 0

    class Meta:
        model = Sale
        fields = ('sale_date', 'label', 'taxable', 'collector1', 'salestax1', 'collector2', 'salestax2',)
