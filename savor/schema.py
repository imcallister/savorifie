import graphene

import savor.inventory.models

class FulfillmentType(graphene.ObjectType):
    request_date = graphene.String(description='Like a phone number, but often longer')
    warehouse = graphene.String()
    order = graphene.String(description='Mostly less strange people')
    ship_type = graphene.String(description='Pretty much all of your name')
    id = graphene.String()
    bill_to = graphene.String()
    

class QueryType(graphene.ObjectType):
    all_fulfillment = graphene.List(FulfillmentType, description='A few billion people')
    fulfillment = graphene.Field(
        FulfillmentType,
        id=graphene.ID(),
        description='Just one person belonging to an ID',
    )

    def resolve_all_fulfillment(self, args, info):
        return savor.inventory.models.Fulfillment.objects.all()
    def resolve_fulfillment(self, args, info):
        id = args.get('id')
        return savor.inventory.models.Fulfillment.objects.get(pk=id)

schema = graphene.Schema(query=QueryType)