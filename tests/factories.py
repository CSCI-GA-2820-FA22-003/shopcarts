"""
Test Factory to make fake objects for testing
"""
from datetime import date

import factory
from factory.fuzzy import FuzzyInteger, FuzzyFloat, FuzzyDate
from service.models import Products, Shopcarts


class ProductsFactory(factory.Factory):
    """Creates fake products"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Products

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    user_id = str(FuzzyInteger(1, 999))
    product_id = str(FuzzyInteger(1, 999))
    quantity = FuzzyFloat(0.01, 99999.0)
    price = FuzzyFloat(0.01, 99999.0)
    time = FuzzyDate(date(2020, 1, 1))


class ShopcartsFactory(factory.Factory):
    """Creates fake shopcarts"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Shopcarts

    id = factory.Sequence(lambda n: n)
    user_id = str(FuzzyInteger(1, 999))
