from inventory.models import Warehouse, Fulfillment, FulfillLine, InventoryItem
from inventory.serializers import WarehouseSerializer, FulfillmentSerializer, FulfillLineSerializer, InventoryItemSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
