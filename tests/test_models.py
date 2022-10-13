"""
Test cases for ShopCarts and Products Model

"""
import os
import logging
import unittest
from datetime import date
from werkzeug.exceptions import NotFound
from service.models import Products, Shopcarts, DataValidationError, db
from service import app
from tests.factories import ProductsFactory, ShopcartsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  M O D E L   T E S T   C A S E S
######################################################################
class TestProductsModel(unittest.TestCase):
    """ Test Cases for Products Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Products.init_db(app)
        Shopcarts.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.drop_all()
        db.create_all()
        db.session.commit()
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Products).delete()  # clean up the last tests
        db.session.query(Shopcarts).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """ It should Create a product and assert that it exists """
        product = Products(name="Pen", user_id="1", product_id="2",
         quantity=1.0, price=12, time=date(2020, 1, 1))
        self.assertEqual(str(product), "<Products Pen in user 1's shopcart>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Pen")
        self.assertEqual(product.user_id, "1")
        self.assertEqual(product.product_id, "2")
        self.assertEqual(product.quantity, 1.0)
        self.assertEqual(product.price, 12)
        self.assertEqual(product.time, date(2020, 1, 1))

    def test_add_a_product(self):
        """It should Create a Product and add it to the database"""
        products = Products.all()
        self.assertEqual(products, [])
        product = Products(name="Pen", user_id="1", product_id="2",
         quantity=1.0, price=12, time=date(2020, 1, 1))
        shopcart = Shopcarts(user_id="1")
        shopcart.create()
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Products.all()
        self.assertEqual(len(products), 1)

    def test_add_a_duplicated_product(self):
        """It should Update instead of Adding a duplicated product"""
        products = Products.all()
        self.assertEqual(products, [])
        product = Products(name="Pen", user_id="1", product_id="2",
         quantity=1.0, price=12, time=date(2020, 1, 1))
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        shopcart = Shopcarts(user_id="1")
        shopcart.create()
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Products.all()
        self.assertEqual(len(products), 1)
        product = Products(name="Pen", user_id="1", product_id="2",
         quantity=1.0, price=12, time=date(2020, 1, 1))
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        # Assert that it was updated in the database instead of adding
        self.assertIsNotNone(product.id)
        products = Products.all()
        self.assertEqual(len(products), 1)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductsFactory()
        logging.debug(product)
        product.id = None
        shopcart = Shopcarts(user_id=product.user_id)
        shopcart.create()
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Products.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.user_id, product.user_id)
        self.assertEqual(found_product.product_id, product.product_id)
        self.assertEqual(found_product.quantity, product.quantity)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.time, product.time)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductsFactory()
        logging.debug(product)
        product.id = None
        shopcart = Shopcarts(user_id=product.user_id)
        shopcart.create()
        product.create()
        self.assertIsNotNone(product.id)
        # Change it an save it
        product.price = 15
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.price, 15)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Products.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].price, 15)

    def test_update_no_id(self):
        """It should not Update a Product with no id"""
        product = ProductsFactory()
        logging.debug(product)
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductsFactory()
        shopcart = Shopcarts(user_id=product.user_id)
        shopcart.create()
        product.create()
        self.assertEqual(len(Products.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Shopcarts.all()), 1)
        self.assertEqual(len(Products.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Products.all()
        self.assertEqual(products, [])
        # Create 5 Pets
        product = Products(name="Pen", user_id="1", product_id="2",
         quantity=1.0, price=12, time=date(2020, 1, 1))
        shopcart = Shopcarts(user_id="1")
        shopcart.create()
        product.create()
        product = Products(name="Pencil", user_id="1", product_id="3",
         quantity=1.0, price=12, time=date(2020, 1, 1))
        product.create()
        product = Products(name="Pig", user_id="1", product_id="4",
         quantity=1.0, price=12, time=date(2020, 1, 1))
        product.create()
        product = Products(name="Food", user_id="1", product_id="1",
         quantity=1.0, price=12, time=date(2020, 1, 1))
        product.create()
        shopcart = Shopcarts(user_id="2")
        shopcart.create()
        product = Products(name="Food", user_id="2", product_id="1",
         quantity=1.0, price=12, time=date(2020, 1, 1))
        product.create()
        # See if we get back 5 products
        products = Products.all()
        self.assertEqual(len(products), 5)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductsFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("user_id", data)
        self.assertEqual(data["user_id"], product.user_id)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], product.product_id)
        self.assertIn("time", data)
        self.assertEqual(date.fromisoformat(data["time"]), product.time)
        self.assertIn("price", data)
        self.assertEqual(data["price"], product.price)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], product.quantity)

    def test_deserialize_a_product(self):
        """It should de-serialize a Product"""
        data = ProductsFactory().serialize()
        product = Products()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.user_id, data["user_id"])
        self.assertEqual(product.product_id, data["product_id"])
        self.assertEqual(product.price, data["price"])
        self.assertEqual(product.quantity, data["quantity"])
        self.assertEqual(product.time, date.fromisoformat(data["time"]))

    def test_deserialize_missing_data(self):
        """It should not deserialize a Product with missing data"""
        data = {"id": 1, "name": "Spoon", "user_id": "1"}
        product = Products()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        product = Products()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductsFactory.create_batch(5)
        for product in products:
            if len(Shopcarts.find_by_user_id(product.user_id).all())==0:
                shopcart = Shopcarts(user_id=product.user_id)
                shopcart.create()
            product.create()
        name = products[0].name
        found = Products.find_by_name(name)
        self.assertEqual(found[0].user_id, products[0].user_id)
        self.assertEqual(found[0].name, products[0].name)
        self.assertEqual(found[0].product_id, products[0].product_id)
        self.assertEqual(found[0].price, products[0].price)
        self.assertEqual(found[0].quantity, products[0].quantity)
        self.assertEqual(found[0].time, products[0].time)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        products = ProductsFactory.create_batch(3)
        for product in products:
            if len(Shopcarts.find_by_user_id(product.user_id).all())==0:
                shopcart = Shopcarts(user_id=product.user_id)
                shopcart.create()
            product.create()

        product = Products.find_or_404(products[0].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[0].id)
        self.assertEqual(product.user_id, products[0].user_id)
        self.assertEqual(product.product_id, products[0].product_id)
        self.assertEqual(product.name, products[0].name)
        self.assertEqual(product.price, products[0].price)
        self.assertEqual(product.quantity, products[0].quantity)
        self.assertEqual(product.time, products[0].time)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Products.find_or_404, 0)

    def test_create_shopcart(self):
        """It should create a shopcart"""
        shopcart = Shopcarts(user_id="1")
        self.assertEqual(str(shopcart), "<Shopcarts 1>")
        self.assertTrue(shopcart is not None)
        self.assertEqual(shopcart.id, None)

    def test_add_shopcart(self):
        """It should create a shopcart and add it to the database"""
        shopcart = Shopcarts(user_id="1")
        self.assertEqual(str(shopcart), "<Shopcarts 1>")
        self.assertTrue(shopcart is not None)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(len(Shopcarts.all()), 0)
        shopcart.create()
        self.assertEqual(len(Shopcarts.all()), 1)

    def test_shopcart_back_ref(self):
        """It should back reference from shopcart to product"""
        product = ProductsFactory()
        shopcart = Shopcarts(user_id=product.user_id)
        shopcart.create()
        product.create()
        self.assertEqual(shopcart.products[0].id, product.id)

    def test_create_duplicated_shopcart(self):
        """It should return error when creating duplicated shopcarts"""
        shopcart = Shopcarts(user_id="1")
        self.assertEqual(str(shopcart), "<Shopcarts 1>")
        self.assertTrue(shopcart is not None)
        self.assertEqual(shopcart.id, None)
        shopcart.create()
        shopcart = Shopcarts(user_id="1")
        self.assertEqual(str(shopcart), "<Shopcarts 1>")
        self.assertTrue(shopcart is not None)
        self.assertEqual(shopcart.id, None)
        self.assertRaises(DataValidationError, shopcart.create)

    def test_delete_a_shopcart(self):
        """It should Delete a Product"""
        product = ProductsFactory()
        shopcart = Shopcarts(user_id=product.user_id)
        shopcart.create()
        product.create()
        self.assertEqual(len(Products.all()), 1)
        self.assertEqual(len(Shopcarts.all()), 1)
        # delete the shopcart and make sure it isn't in the database
        shopcart.delete()
        self.assertEqual(len(Shopcarts.all()), 0)
        self.assertEqual(len(Products.all()), 0)

    def test_serialize_a_shopcart(self):
        """It should serialize a Shopcart"""
        shopcart = ShopcartsFactory()
        data = shopcart.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], shopcart.id)
        self.assertIn("user_id", data)
        self.assertEqual(data["user_id"], shopcart.user_id)
        self.assertIn("products", data)
        self.assertEqual(data["products"], shopcart.products)

    def test_deserialize_a_shopcart(self):
        """It should de-serialize a Shopcart"""
        data = ShopcartsFactory().serialize()
        shopcart = Shopcarts()
        shopcart.deserialize(data)
        self.assertNotEqual(shopcart, None)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.user_id, data["user_id"])

    def test_deserialize_missing_shopcart_data(self):
        """It should not deserialize a Shopcart with missing data"""
        data = {"id": 1}
        shopcart = Shopcarts()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_deserialize_bad_shopcart_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        shopcart = Shopcarts()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_update_a_shopcart(self):
        """It should Update a Shopcart"""
        shopcart = ShopcartsFactory()
        logging.debug(shopcart)
        shopcart.id = None
        shopcart.create()
        old_product = Products(user_id=shopcart.user_id, product_id="1", name="Pen",
         price=1, time=date(2011,1,2), quantity=1)
        old_product.create()
        old_products = []
        old_products.append(old_product)
        self.assertEqual(shopcart.products, old_products)
        self.assertIsNotNone(shopcart.id)
        # Change it an save it
        new_products = []
        new_products.append(Products(user_id=shopcart.user_id, product_id="2", name="Pig",
         price=1, time=date(2011,1,2), quantity=1))
        for old_product in shopcart.products:
            old_product.delete()
        original_id = shopcart.id
        for product in new_products:
            product.create()
        self.assertEqual(shopcart.id, original_id)
        self.assertEqual(shopcart.products, new_products)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        shopcarts = Shopcarts.all()
        self.assertEqual(len(shopcarts), 1)
        self.assertEqual(shopcarts[0].id, original_id)
        self.assertEqual(shopcarts[0].products, new_products)

    def test_update_shopcart_no_id(self):
        """It should not Update a Shopcart with no id"""
        shopcart = ShopcartsFactory()
        logging.debug(shopcart)
        shopcart.id = None
        self.assertRaises(DataValidationError, shopcart.update)

    def test_find_or_404_found_shopcart(self):
        """It should Find or return 404 not found"""
        shopcarts = ShopcartsFactory.create_batch(3)
        for shopcart in shopcarts:
            if len(Shopcarts.find_by_user_id(shopcart.user_id).all())==0:
                shopcart.create()
                for product in shopcart.products:
                    product.create()
            else:
                for old_product in Shopcarts.find_by_user_id(shopcart.user_id).all()[0].products:
                    old_product.delete()
                for product in shopcart.products:
                    product.create()

        shopcart = Shopcarts.find_or_404(shopcarts[0].id)
        self.assertIsNot(shopcart, None)
        self.assertEqual(shopcart.id, shopcarts[0].id)
        self.assertEqual(shopcart.products, shopcarts[0].products)
        self.assertEqual(shopcart.user_id, shopcarts[0].user_id)

    def test_find_or_404_not_found_shopcart(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Shopcarts.find_or_404, 0)

    def test_read_a_shopcart(self):
        """It should Read a Shopcart"""
        shopcart = ShopcartsFactory()
        logging.debug(shopcart)
        shopcart.id = None
        shopcart.create()
        for product in shopcart.products:
            product.create()
        self.assertIsNotNone(shopcart.id)
        # Fetch it back
        found_shopcart = Shopcarts.find(shopcart.id)
        self.assertEqual(found_shopcart.id, shopcart.id)
        self.assertEqual(found_shopcart.user_id, shopcart.user_id)
        self.assertEqual(found_shopcart.products, shopcart.products)
