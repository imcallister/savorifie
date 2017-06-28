from accountifie.common.serializers import EagerLoadingMixin

from ..models import PayoutLine
from rest_framework import serializers


class PayoutLineSerializer(serializers.ModelSerializer, EagerLoadingMixin):
    _SELECT_RELATED_FIELDS = ['sale__channel__counterparty']

    sale = serializers.StringRelatedField()

    class Meta:
        model = PayoutLine
        fields = ('sale', 'amount', 'tag',)
