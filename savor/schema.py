import graphene
from graphene.contrib.django import DjangoNode
from django.db.models import Prefetch

import savor.inventory.models
import savor.base.models

"""
class FulfillmentType(graphene.ObjectType):
    request_date = graphene.String(description='Like a phone number, but often longer')
    warehouse = graphene.String()
    order = graphene.String(description='Mostly less strange people')
    ship_type = graphene.String(description='Pretty much all of your name')
    id = graphene.String()
    bill_to = graphene.String()
"""

class SaleNode(DjangoNode):
    class Meta:
        model = savor.base.models.Sale

    @classmethod
    def get_node(cls, id, info):
        return SaleNode(savor.base.models.Sale.objects.get(pk=id))


class FulfillmentNode(DjangoNode):

    class Meta:
        model = savor.inventory.models.Fulfillment

    @classmethod
    def get_node(cls, id, info):
        return FulfillmentNode(savor.inventory.models.Fulfillment.objects.all().prefetch_related(Prefetch('fulfillupdate_set', to_attr='updates')).filter(pk=id)).first()


class FulfillUpdateNode(DjangoNode):

    class Meta:
        model = savor.inventory.models.FulfillUpdate

    @classmethod
    def get_node(cls, id, info):
        return FulfillUpdateNode(savor.inventory.models.Fulfillment.objects.prefetch_related(Prefetch('fulfillupdate_set', to_attr='updates')).get(pk=id))



class QueryType(graphene.ObjectType):
    all_fulfillment = graphene.List(FulfillmentNode, description='A few billion people')
    all_sale = graphene.List(SaleNode, description='A few billion people')
    fulfillment = graphene.Field(
        FulfillmentNode,
        id=graphene.ID(),
        description='Just one person belonging to an ID',
    )
    sale = graphene.Field(
        SaleNode,
        id=graphene.ID(),
        description='Just one person belonging to an ID',
    )

    def resolve_all_fulfillment(self, args, info):
        qs = savor.inventory.models.Fulfillment.objects.all().prefetch_related(Prefetch('fulfillupdate_set', to_attr='updates'))
        return qs

    def resolve_fulfillment(self, args, info):
        id = args.get('id')
        return savor.inventory.models.Fulfillment.objects.prefetch_related(Prefetch('fulfillupdate_set', to_attr='updates')).get(pk=id)

    def resolve_all_fulfillupdate(self, args, info):
        return savor.inventory.models.FulfillUpdate.objects.all()

    def resolve_fulfillupdate(self, args, info):
        id = args.get('id')
        return savor.inventory.models.FulfillUpdate.objects.get(pk=id)

    def resolve_all_sale(self, args, info):
        return savor.base.models.Sale.objects.all()

    def resolve_sale(self, args, info):
        id = args.get('id')
        return savor.base.models.Sale.objects.get(pk=id)


schema = graphene.Schema(query=QueryType)