"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db, Products, Shopcarts, init_db
from service.common import status
from tests.factories import ShopcartsFactory  # HTTP Status Codes

TEST_USER = "foo"
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  T E S T   C A S E S
######################################################################
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
        """Factory method to create pets in bulk"""
        shopcarts = []
        for i in range(count):
            test_shopcart = Shopcarts(user_id=str(i))
            response = self.app.post("/shopcarts", json=test_shopcart.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test shopcart"
            )
            new_shopcart = response.get_json()
            test_shopcart.id = new_shopcart["id"]
            shopcarts.append(test_shopcart)
        return shopcarts

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

    def test_read_shopcarts(self):
        """ It should Read a Shopcart """
        shopcart = ShopcartsFactory()
        logging.debug("Test Shopcart: %s", shopcart.serialize())
        self.app.post("/shopcarts", json=shopcart.serialize())
        resp = self.app.get(f"/shopcarts/{shopcart.user_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["user_id"], shopcart.user_id)

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

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_shopcart_no_data(self):
        """It should not Create a Shopcart with missing data"""
        response = self.app.post("/shopcarts", json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pet_no_content_type(self):
        """It should not Create a Shopcart with no content type"""
        response = self.app.post("/shopcarts")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_pet_no_content_type_with_header(self):
        """It should not Create a Shopcart with no content type"""
        response = self.app.post("/shopcarts", headers={"Content-Type": "application/haha"})
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
