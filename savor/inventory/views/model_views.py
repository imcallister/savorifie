from inventory.models import Warehouse, Fulfillment
from inventory.serializers import WarehouseSerializer, FulfillmentSerializer
from rest_framework import generics


# note can call from other views with
# WarehouseList.as_view()(factory.get('/warehouse', format='json')).data

class WarehouseList(generics.ListCreateAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class WarehouseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class FulfillmentList(generics.ListCreateAPIView):
    queryset = Fulfillment.objects.all()
    serializer_class = FulfillmentSerializer


class FulfillmentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fulfillment.objects.all()
    serializer_class = FulfillmentSerializer
