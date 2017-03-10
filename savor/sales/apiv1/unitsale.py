from ..models import UnitSale
from sales.serializers import UnitSaleSerializer, UnitSaleItemSerializer
from accounting.serializers import COGSAssignmentSerializer


def unitsale( qstring):
    qs = UnitSale.objects.all()
    qs = UnitSaleSerializer.setup_eager_loading(qs)
    return UnitSaleSerializer(qs, many=True).data


def unitsaleitems( qstring):
    qs = UnitSale.objects.all()
    qs = UnitSaleItemSerializer.setup_eager_loading(qs)
    return UnitSaleItemSerializer(qs, many=True).data


def unitsale_COGS(unitsale_id, qstring):
    qs = UnitSale.objects.get(id=unitsale_id).cogsassignment_set.all()
    return COGSAssignmentSerializer(qs, many=True).data
