"""
Test Factory to make fake objects for testing
"""
from datetime import date

import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Products


class ProductsFactory(factory.Factory):
    """Creates fake products"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Products

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    user_id = FuzzyChoice(choices=["1", "2", "3", "4"])
    product_id = FuzzyChoice(choices=["1", "2", "3", "4"])
    quantity = FuzzyChoice(choices=[1.0, 2.0, 3.0, 4.0])
    price = FuzzyChoice(choices=[1.0, 2.0, 3.0, 4.0])
    time = FuzzyDate(date(2020, 1, 1))
