"""
Test cases for ShopCarts and Products Model

"""
import os
import logging
import unittest
from datetime import date
from werkzeug.exceptions import NotFound
from service.models import Products, DataValidationError, db
from service import app
from tests.factories import ProductsFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Products   M O D E L   T E S T   C A S E S
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

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        db.session.query(Products).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """ It should Create a product and assert that it exists """
        product = Products(name="Pen", userId="1", productId="2", quantity=1.0, price=12, time=date(2020, 1, 1))
        self.assertEqual(str(product), "<Products Pen in user 1's shopcart>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Pen")
        self.assertEqual(product.userId, "1")
        self.assertEqual(product.productId, "2")
        self.assertEqual(product.quantity, 1.0)
        self.assertEqual(product.price, 12)
        self.assertEqual(product.time, date(2020, 1, 1))

    def test_add_a_product(self):
        """It should Create a Product and add it to the database"""
        products = Products.all()
        self.assertEqual(products, [])
        product = Products(name="Pen", userId="1", productId="2", quantity=1.0, price=12, time=date(2020, 1, 1))
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
        product = Products(name="Pen", userId="1", productId="2", quantity=1.0, price=12, time=date(2020, 1, 1))
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Products.all()
        self.assertEqual(len(products), 1)
        product = Products(name="Pen", userId="1", productId="2", quantity=1.0, price=12, time=date(2020, 1, 1))
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
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Products.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.userId, product.userId)
        self.assertEqual(found_product.productId, product.productId)
        self.assertEqual(found_product.quantity, product.quantity)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.time, product.time)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductsFactory()
        logging.debug(product)
        product.id = None
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
        product.create()
        self.assertEqual(len(Products.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Products.all()), 0)
    
    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Products.all()
        self.assertEqual(products, [])
        # Create 5 Pets
        product = Products(name="Pen", userId="1", productId="2", quantity=1.0, price=12, time=date(2020, 1, 1))
        product.create()
        product = Products(name="Pencil", userId="1", productId="3", quantity=1.0, price=12, time=date(2020, 1, 1))
        product.create()
        product = Products(name="Pig", userId="1", productId="4", quantity=1.0, price=12, time=date(2020, 1, 1))
        product.create()
        product = Products(name="Food", userId="1", productId="1", quantity=1.0, price=12, time=date(2020, 1, 1))
        product.create()
        product = Products(name="Food", userId="2", productId="1", quantity=1.0, price=12, time=date(2020, 1, 1))
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
        self.assertIn("userId", data)
        self.assertEqual(data["userId"], product.userId)
        self.assertIn("productId", data)
        self.assertEqual(data["productId"], product.productId)
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
        self.assertEqual(product.userId, data["userId"])
        self.assertEqual(product.productId, data["productId"])
        self.assertEqual(product.price, data["price"])
        self.assertEqual(product.quantity, data["quantity"])
        self.assertEqual(product.time, date.fromisoformat(data["time"]))

    def test_deserialize_missing_data(self):
        """It should not deserialize a Product with missing data"""
        data = {"id": 1, "name": "Spoon", "userId": "1"}
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
            product.create()
        name = products[0].name
        found = Products.find_by_name(name)
        self.assertEqual(found.count(), 1)
        self.assertEqual(found[0].userId, products[0].userId)
        self.assertEqual(found[0].name, products[0].name)
        self.assertEqual(found[0].productId, products[0].productId)
        self.assertEqual(found[0].price, products[0].price)
        self.assertEqual(found[0].quantity, products[0].quantity)
        self.assertEqual(found[0].time, products[0].time)
    
    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        products = ProductsFactory.create_batch(3)
        for product in products:
            product.create()

        product = Products.find_or_404(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.userId, products[1].userId)
        self.assertEqual(product.productId, products[1].productId)
        self.assertEqual(product.name, products[1].name)
        self.assertEqual(product.price, products[1].price)
        self.assertEqual(product.quantity, products[1].quantity)
        self.assertEqual(product.time, products[1].time)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Products.find_or_404, 0)
