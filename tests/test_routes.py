"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from datetime import date
from unittest import TestCase
# from unittest.mock import MagicMock, patch
from service import app
from service.models import db, Products, Shopcarts, DataValidationError, init_db
from service.common import status
from tests.factories import ShopcartsFactory  # HTTP Status Codes
from tests.factories import ProductsFactory

TEST_USER = "foo"
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  T E S T   C A S E S
######################################################################


# pylint: disable=too-many-public-methods
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.drop_all()
        db.create_all()
        db.session.commit()
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()
        db.session.query(Products).delete()  # clean up the last tests
        db.session.query(Shopcarts).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    def _create_shopcarts(self, count):
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for i in range(count):
            test_shopcart = ShopcartsFactory()
            test_shopcart.user_id = str(i)
            response = self.app.post("/shopcarts", json=test_shopcart.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test shopcart"
            )
            new_shopcart = response.get_json()
            test_shopcart.id = new_shopcart["id"]
            shopcarts.append(test_shopcart)
        return shopcarts

    def _make_products(self, count, user_id):
        """Factory method to create products in bulk under one user_id"""
        products = []
        for i in range(count):
            test_product = ProductsFactory()
            test_product.user_id = user_id
            test_product.product_id = str(i)
            products.append(test_product.serialize())
        return products

    def _create_products(self, count, user_id):
        """Factory method to create products in bulk under one user_id"""
        products = []
        for i in range(count):
            test_product = ProductsFactory()
            test_product.user_id = user_id
            test_product.product_id = str(i)
            response = self.app.post(f"/shopcarts/{user_id}/items", json=test_product.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_shopcarts(self):
        """ It should Create a Shopcart """
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        resp = self.app.post("/shopcarts", json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["user_id"], shopcart.user_id)

    def test_create_shopcarts_409_conflicts(self):
        """ It should return a 409_conflicts """
        shopcart = ShopcartsFactory()
        resp = self.app.post("/shopcarts", json=shopcart.serialize())
        resp = self.app.post("/shopcarts", json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_read_shopcarts(self):
        """ It should Read a Shopcart """
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        self.app.post("/shopcarts", json=shopcart.serialize())
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["user_id"], shopcart.user_id)

    def test_update_shopcart_404_not_found(self):
        """ It should return a 404 not found """
        shopcart = ShopcartsFactory()

        # create a shopcart
        self.app.post("/shopcarts", json=shopcart.serialize())

        # make product data
        product_num = 100
        products = self._make_products(2*product_num, shopcart.user_id)

        # update old shopcart
        resp = self.app.put(f"/shopcarts/{shopcart.user_id}+10", json=products[:product_num])
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_shopcart(self):
        """ It should update a Shopcart """
        shopcart = ShopcartsFactory()

        # create a shopcart
        self.app.post("/shopcarts", json=shopcart.serialize())

        # make product data
        product_num = 5
        products = self._make_products(2*product_num, shopcart.user_id)

        # update old shopcart
        resp = self.app.put(f"/shopcarts/{shopcart.user_id}", json=products[:product_num])
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # update shopcart
        resp = self.app.put(f"/shopcarts/{shopcart.user_id}", json=products[product_num:])
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # get updated shopcart items
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        newdata = resp.get_json()

        # check whether the products have been added
        self.assertEqual(len(newdata), product_num)
        for i in range(1, product_num+1):
            curr_newdata = newdata[-i]
            curr_product = Products()
            curr_product.deserialize(products[-i])
            self.assertEqual(curr_newdata["user_id"], curr_product.user_id)
            self.assertEqual(curr_newdata["product_id"], curr_product.product_id)
            self.assertEqual(curr_newdata["name"], curr_product.name)
            self.assertEqual(curr_newdata["time"], curr_product.time.isoformat())
            self.assertEqual(curr_newdata["quantity"], curr_product.quantity)
            self.assertEqual(curr_newdata["price"], curr_product.price)

    def test_delete_shopcarts(self):
        """ It should Delete a Shopcart """
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        self.app.post("/shopcarts", json=shopcart.serialize())
        products = self._create_products(1, shopcart.user_id)
        product = products[0]
        resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Products.all()), 1)
        resp = self.app.delete(f"/shopcarts/{shopcart.user_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure shopcart is deleted
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        # make sure product is deleted
        self.assertEqual(len(Products.all()), 0)

    def test_list_all_products_404_not_found(self):
        """ It should return a 404 not found """
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart 404 not found: %s", shopcart.serialize())
        self.app.post("/shopcarts", json=shopcart.serialize())
        products = self._create_products(5, shopcart.user_id)
        for product in products:
            resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}+10/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_shopcart_not_found(self):
        """It should not Get a Shopcart thats not found"""
        response = self.app.get("/shopcarts/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_get_shopcart_list(self):
        """It should Get a list of Shopcarts"""
        self._create_shopcarts(5)
        response = self.app.get("/shopcarts")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_create_products(self):
        """ It should Create a Shopcart and add products to it"""
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        resp = self.app.post("/shopcarts", json=shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["user_id"], shopcart.user_id)
        products = self._create_products(5, shopcart.user_id)
        for product in products:
            resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
            data = resp.get_json()
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            self.assertEqual(data["user_id"], product.user_id)
            self.assertEqual(data["product_id"], product.product_id)
            self.assertEqual(data["name"], product.name)

    def test_read_a_product(self):
        """ It should Read a Product """
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        self.app.post("/shopcarts", json=shopcart.serialize())
        products = self._create_products(5, shopcart.user_id)
        for product in products:
            resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            resp = self.app.get(f"/shopcarts/{shopcart.user_id}/items/{product.product_id}")
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            data = resp.get_json()
            self.assertEqual(data["user_id"], product.user_id)
            self.assertEqual(data["product_id"], product.product_id)
            self.assertEqual(data["name"], product.name)

    def test_get_product_not_found(self):
        """It should not Get a Product thats not found"""
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        self.app.post("/shopcarts", json=shopcart.serialize())
        response = self.app.get(f"/shopcarts/{shopcart.user_id}/items/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_list_all_products(self):
        """ It should Read all Products """
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        self.app.post("/shopcarts", json=shopcart.serialize())
        products = self._create_products(5, shopcart.user_id)
        for product in products:
            resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}/items")
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_update_a_product(self):
        """ It should Update a Product """
        shopcart = ShopcartsFactory()
        self.app.post("/shopcarts", json=shopcart.serialize())
        products = self._create_products(1, shopcart.user_id)
        product = products[0]
        resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_product = Products(user_id=product.user_id, product_id=product.product_id, price=15.0,
                               time=date.today(), quantity=16.0, name="new")
        resp = self.app.put(f"/shopcarts/{shopcart.user_id}/items/{product.product_id}",
                            json=new_product.serialize())
        data = resp.get_json()
        self.assertEqual(data["user_id"], new_product.user_id)
        self.assertEqual(data["product_id"], new_product.product_id)
        self.assertEqual(data["name"], new_product.name)
        self.assertEqual(data["time"], new_product.time.isoformat())
        self.assertEqual(data["quantity"], new_product.quantity)
        self.assertEqual(data["price"], new_product.price)
        # Fetch it back
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}/items/{product.product_id}",
                            json=new_product.serialize())
        data = resp.get_json()
        self.assertEqual(data["user_id"], new_product.user_id)
        self.assertEqual(data["product_id"], new_product.product_id)
        self.assertEqual(data["name"], new_product.name)
        self.assertEqual(data["time"], new_product.time.isoformat())
        self.assertEqual(data["quantity"], new_product.quantity)
        self.assertEqual(data["price"], new_product.price)

    def test_delete_a_product(self):
        """ It should Delete a Product from the shopcart """
        shopcart = ShopcartsFactory()
        self.app.post("/shopcarts", json=shopcart.serialize())
        products = self._create_products(1, shopcart.user_id)
        product = products[0]
        resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Products.all()), 1)
        resp = self.app.delete(f"/shopcarts/{shopcart.user_id}/items/{product.product_id}")
        self.assertEqual(len(Products.all()), 0)
        # make sure the product is deleted
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}/items/{product.product_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_products(self):
        """ It should Return Products satisfied the query """
        shopcart = ShopcartsFactory()
        self.app.post("/shopcarts", json=shopcart.serialize())
        product = Products(user_id=shopcart.user_id, product_id="1", name="Pen",
                           price=4, time=date(2011, 1, 2), quantity=1)
        resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Products.all()), 1)
        product = Products(user_id=shopcart.user_id, product_id="2", name="Pencil",
                           price=2, time=date(2011, 1, 2), quantity=1)
        resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Products.all()), 2)
        product = Products(user_id=shopcart.user_id, product_id="3", name="Melon",
                           price=6, time=date(2011, 1, 2), quantity=1)
        resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Products.all()), 3)
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}/items")
        self.assertEqual(len(resp.get_json()), 3)
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}/items?max-price=9&min-price=5")
        self.assertEqual(len(resp.get_json()), 1)
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}/items?max-price=5&min-price=1")
        self.assertEqual(len(resp.get_json()), 2)

    def test_empty_shopcarts(self):
        """ It should Empty a Shopcart """
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        self.app.post("/shopcarts", json=shopcart.serialize())
        products = self._create_products(1, shopcart.user_id)
        product = products[0]
        resp = self.app.post(f"/shopcarts/{shopcart.user_id}/items", json=product.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Products.all()), 1)
        resp = self.app.put(f"/shopcarts/{shopcart.user_id}/empty")
        self.assertEqual(resp.get_json()["products"], [])
        self.assertEqual(len(Products.all()), 0)
        # make sure shopcart is deleted
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}")
        data = resp.get_json()
        self.assertEqual(data["products"], [])

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_shopcart_no_data(self):
        """It should not Create a Shopcart with missing data"""
        shopcart = Shopcarts()
        self.assertRaises(DataValidationError, shopcart.create)

    def test_create_shopcart_no_content_type(self):
        """It should not Create a Shopcart with no content type"""
        response = self.app.post("/shopcarts")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_shopcart_wrong_content_type(self):
        """It should not Create a Shopcart with wrong content type"""
        response = self.app.post("/shopcarts", headers={"Content-Type": "application/haha"})
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_unsupported_method(self):
        """It should not alloww unsupported methods"""
        response = self.app.put("/shopcarts")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
