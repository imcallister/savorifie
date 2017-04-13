from django.utils.safestring import mark_safe

from accountifie.common.serializers import EagerLoadingMixin

from ..models import Sale, Payout
from unitsale_serializers import UnitSaleSerializer
from rest_framework import serializers



class SaleIDSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    
    class Meta:
        model = Sale
        fields = ('external_channel_id',)


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


class SaleGrossProceedsSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    gross_proceeds = serializers.DecimalField(max_digits=9, decimal_places=2)
    
    _PREFETCH_RELATED_FIELDS = ['unit_sale__sku__skuunit__inventory_item']

    class Meta:
        model = Sale
        fields = ('id', 'gross_proceeds',)


class SaleProceedsAdjustmentSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    total_adjustments = serializers.DecimalField(max_digits=9, decimal_places=2)
    
    _PREFETCH_RELATED_FIELDS = ['proceedsadjustment_sale']

    class Meta:
        model = Sale
        fields = ('id','total_adjustments',)


class SalePayoutsSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    total_payout = serializers.DecimalField(max_digits=9, decimal_places=2)
    
    _PREFETCH_RELATED_FIELDS = ['payoutline_sale']

    class Meta:
        model = Sale
        fields = ('id', 'total_payout',)


class SalesTaxSerializer3(serializers.ModelSerializer, EagerLoadingMixin):
    total_salestax = serializers.DecimalField(max_digits=9, decimal_places=2)
    
    _PREFETCH_RELATED_FIELDS = ['sales_tax']

    class Meta:
        model = Sale
        fields = ('id', 'total_salestax',)


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
        unf = obj.unfulfilled_items
        if unf:
            items = [(k, v) for k, v in unf.iteritems()]
            items = sorted(items, key=lambda x: x[0])
            return ','.join(['%s %s' % (i[1], i[0]) for i in items])
        else:
            return ''


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
                  'shipping_zip', 'shipping_province', 'items_string', 'unfulfilled_string', 'unfulfilled_items',
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
                  'external_channel_id', 'special_sale',
                  'gift_wrapping', 'gift_wrap_fee',
                  'gift_message', 'external_routing_id',
                  'notification_email', 'shipping_name',
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
                  'external_channel_id', 'special_sale',
                  'gift_wrapping', 'gift_wrap_fee',
                  'gift_message', 'memo', 'external_routing_id',
                  'notification_email', 'shipping_name',
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

