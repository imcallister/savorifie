import factory
from .models import Sale, UnitSale

class SaleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Sale

    id = 'TEST_COMPANY'
    name = 'Test Company'
    cmpy_type = 'ALO'


class UnitSaleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UnitSale

class SalesTaxFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SalesTax
