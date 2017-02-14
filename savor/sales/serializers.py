from django.utils.safestring import mark_safe

from accountifie.common.serializers import EagerLoadingMixin

from .models import UnitSale, Sale, SalesTax, ChannelPayouts, Payout
from rest_framework import serializers


class UnitSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['sku__label', 'sku__description']
    sku = serializers.StringRelatedField()

    class Meta:
        model = UnitSale
        fields = ('id', 'sale', 'sku', 'quantity', 'unit_price')


class UnitSaleItemSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['sku__label', 'sku__description']
    _PREFETCH_RELATED_FIELDS = ['sku__skuunit', 'sku__skuunit__inventory_item']
    
    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        return dict((i.inventory_item.label, obj.quantity * i.quantity) for i in obj.sku.skuunit.all())

    class Meta:
        model = UnitSale
        fields = ('id', 'sale', 'items', 'unit_price')


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


class SimpleSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    items_string = serializers.SerializerMethodField()

    _SELECT_RELATED_FIELDS = ['channel__counterparty', 'channel', 'customer_code']
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item']

    def get_label(self, obj):
        return str(obj)

    def get_items_string(self, obj):
        return obj.items_string

    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = Sale
        fields = ('id', 'label', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'shipping_name',
                  'shipping_company', 'shipping_zip', 'items_string')


class SaleProceedsSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    proceeds = serializers.SerializerMethodField()
    items_string = serializers.SerializerMethodField()

    _SELECT_RELATED_FIELDS = ['channel__counterparty', 'paid_thru', 'channel', 'customer_code']
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item']

    def get_proceeds(self, obj):
        return obj.total_receivable()

    def get_label(self, obj):
        return str(obj)

    def get_items_string(self, obj):
        return obj.items_string

    channel = serializers.StringRelatedField()
    paid_thru = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = Sale
        fields = ('id', 'label', 'customer_code', 'channel', 'paid_thru', 'sale_date',
                  'external_channel_id', 'shipping_name', 'proceeds',
                  'shipping_company', 'items_string')


class SaleFulfillmentSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    items_string = serializers.SerializerMethodField()
    unfulfilled_items = serializers.SerializerMethodField()
    unfulfilled_string = serializers.SerializerMethodField()
    drilldown = serializers.SerializerMethodField()
    fulfillment_ids = serializers.SerializerMethodField()

    _SELECT_RELATED_FIELDS = ['channel__counterparty', 'channel', 'customer_code']
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item', 'fulfillments__fulfill_lines__inventory_item']

    def get_label(self, obj):
        return str(obj)

    def get_items_string(self, obj):
        return obj.items_string

    def get_unfulfilled_string(self, obj):
        return obj.unfulfilled_items_string

    def get_unfulfilled_items(self, obj):
        return obj.unfulfilled_items

    def get_fulfillment_ids(self, obj):
        return [f.id for f in obj.fulfillments.all()]

    def get_drilldown(self, obj):
        return mark_safe('<a href="/order/drilldown/%s">%s</a>' % (obj.id, obj.label))

    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = Sale
        fields = ('id', 'label', 'customer_code', 'channel', 'sale_date', 'drilldown',
                  'external_channel_id', 'shipping_name', 'shipping_company', 'shipping_city',
                  'shipping_zip', 'items_string', 'unfulfilled_string', 'unfulfilled_items',
                  'fulfillment_ids', 'gift_wrapping'
                  )


class ShippingSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):

    def get_label(self, obj):
        return str(obj)

    _SELECT_RELATED_FIELDS = ['channel__counterparty', 'customer_code']
    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()

    class Meta:
        model = Sale
        fields = ('id', 'label', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'special_sale', 'discount',
                  'discount_code', 'gift_wrapping', 'gift_wrap_fee',
                  'gift_message', 'external_routing_id',
                  'shipping_charge', 'notification_email', 'shipping_name',
                  'shipping_company', 'shipping_address1', 'shipping_address2',
                  'shipping_city', 'shipping_zip', 'shipping_province',
                  'shipping_country', 'shipping_phone')


class FullSaleSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    items_string = serializers.SerializerMethodField()

    def get_label(self, obj):
        return str(obj)

    def get_items_string(self, obj):
        return obj.items_string

    _SELECT_RELATED_FIELDS = ['company', 'channel__counterparty', 'customer_code']
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item']
    company = serializers.StringRelatedField()
    channel = serializers.StringRelatedField()
    customer_code = serializers.StringRelatedField()
    unit_sale = UnitSaleSerializer(many=True)

    class Meta:
        model = Sale
        fields = ('id', 'label', 'company', 'customer_code', 'channel', 'sale_date',
                  'external_channel_id', 'special_sale', 'discount',
                  'discount_code', 'gift_wrapping', 'gift_wrap_fee',
                  'gift_message', 'memo', 'external_routing_id',
                  'shipping_charge', 'notification_email', 'shipping_name',
                  'shipping_company', 'shipping_address1', 'shipping_address2',
                  'shipping_city', 'shipping_zip', 'shipping_province',
                  'shipping_country', 'shipping_phone', 'items_string', 'unit_sale')


class PayoutSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    calcd_payout = serializers.SerializerMethodField()
    diff = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    
    def get_label(self, obj):
        return str(obj)

    def get_calcd_payout(self, obj):
        return obj.calcd_payout()

    def get_diff(self, obj):
        return obj.payout - obj.calcd_payout()

    class Meta:
        model = Payout
        fields = ('label', 'payout_date', 'channel', 'payout', 'calcd_payout', 'diff')



class ChannelPayoutSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    calcd_payout = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    diff = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    def get_label(self, obj):
        return str(obj)

    def get_calcd_payout(self, obj):
        return obj.calcd_payout()

    def get_date(self, obj):
        return obj.payout_date.strftime('%d-%b-%Y')

    def get_diff(self, obj):
        return obj.payout - obj.calcd_payout()

    _SELECT_RELATED_FIELDS = ['channel__counterparty',]
    _PREFETCH_RELATED_FIELDS = ['sales__unit_sale__sku__skuunit__inventory_item',
                                'sales__sales_tax__collector', 'sales__channel__counterparty']

    class Meta:
        model = ChannelPayouts
        fields = ('id', 'date', 'label', 'channel', 'payout', 'calcd_payout', 'diff')

