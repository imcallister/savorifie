from accountifie.common.serializers import EagerLoadingMixin

from ..models import  Payout
from rest_framework import serializers


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

