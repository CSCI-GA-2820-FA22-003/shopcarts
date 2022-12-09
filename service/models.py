"""
Models for Products

All of the models are stored in this module
"""
import logging
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Products.init_db(app)
    Shopcarts.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class DatabaseConnectionError(Exception):
    """Custom Exception when database connection fails"""


class Shopcarts(db.Model):
    """
    Class that represents a Shopcart
    """
    # Table Schema
    __tablename__ = "shopcarts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(63), nullable=False, unique=True)
    products = db.relationship("Products", backref="products", lazy=True)

    def __repr__(self):
        return f"<Shopcarts {self.user_id}>"

    def create(self):
        """
        Creates a Shopcart and add it to the database
        """
        if self.user_id is None:  # user_id is the only required field
            raise DataValidationError("user_id attribute is not set")
        logger.info("Creating %s", self.user_id)
        shopcarts = self.find_by_user_id(self.user_id)
        if len(shopcarts.all()) > 0:
            raise DataValidationError("Shopcart already exists")
        # pylint: disable=invalid-name
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Shopcart in the database
        """
        logger.info("Saving %s", self.user_id)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a Shopcart from the data store """
        logger.info("Deleting %s", self.user_id)
        products_in_shopcart = self.products
        for product in products_in_shopcart:
            logger.info("Deleting %s", product.name)
            db.session.delete(product)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Shopcart into a dictionary """
        product_list = []
        for product in self.products:
            product_list.append(product.serialize())
        return {
            "id": self.id,
            "user_id": self.user_id,
            "products": product_list
            }

    def deserialize(self, data):
        """
        Deserializes a Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.user_id = data["user_id"]
            if "products" in data:
                self.products = data["products"]
            else:
                self.products = []
        except KeyError as error:
            raise DataValidationError(
                "Invalid Products: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Products: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self

    def empty(self):
        """
        Empty a Shopcart
        """
        logger.info("Emptying %s", self.user_id)
        products_in_shopcart = self.products
        for product in products_in_shopcart:
            logger.info("Deleting %s", product.name)
            db.session.delete(product)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app

    @classmethod
    def find_by_user_id(cls, user_id):
        """Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        logger.info("Processing name query for %s ...", user_id)
        return cls.query.filter(cls.user_id == user_id)

    @classmethod
    def all(cls):
        """ Returns all of the Products in the database """
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Shopcart by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, user_id):
        """Find a Shopcart by it's id
        :param user_id: the id of the shopcart to find
        :type user_id: Int
        :return: an instance with the id, or 404_NOT_FOUND if not found
        :rtype: Shopcarts
        """
        logger.info("Processing lookup or 404 for id %s ...", user_id)
        return cls.query.get_or_404(user_id)


class Products(db.Model):
    """
    Class that represents a Products
    """
    # Table Schema
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(63), db.ForeignKey("shopcarts.user_id"), nullable=False)
    product_id = db.Column(db.String(63), nullable=False)
    name = db.Column(db.String(63), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    time = db.Column(db.Date, nullable=False, default=date.today())

    def __repr__(self):
        return f"<Products {self.name} in user {self.user_id}'s shopcart>"

    def create(self):
        """
        Creates a Products to the database
        """
        products = self.find_by_user_id_product_id(self.user_id, self.product_id)
        if len(products.all()) > 0:
            logger.info("Saving %s", self.name)
            self.id = products.all()[0].id  # pylint: disable=invalid-name
            db.session.commit()
        else:
            logger.info("Creating %s", self.name)
            self.id = None  # id must be none to generate next primary key
            db.session.add(self)
            db.session.commit()

    def update(self):
        """
        Updates a Products to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a Products from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Products into a dictionary """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "name": self.name,
            "quantity": self.quantity,
            "price": self.price,
            "time": self.time.isoformat()
            }

    def deserialize(self, data):
        """
        Deserializes a Products from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.user_id = data["user_id"]
            self.product_id = data["product_id"]
            self.name = data["name"]
            self.quantity = float(data["quantity"])
            self.price = float(data["price"])
            self.time = date.fromisoformat(data["time"])
        except KeyError as error:
            raise DataValidationError(
                "Invalid Products: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Products: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error

        if self.price < 0:
            raise DataValidationError("Price should not be negative")

        if self.quantity <= 0:
            raise DataValidationError("Quantity should be positive")

        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Products in the database """
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Products by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_user_id_product_id(cls, user_id, product_id):
        """Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        logger.info("Processing user_id and product_id query for %s and %s ...",
                    user_id, product_id)
        return cls.query.filter(
            and_(
                cls.user_id == user_id,
                cls.product_id == product_id
            )
        )

    @classmethod
    def find_or_404(cls, product_id):
        """Find a Product by it's id
        :param product_id: the id of the Product to find
        :type product_id: Int
        :return: an instance with the product_id, or 404_NOT_FOUND if not found
        :rtype: Products
        """
        logger.info("Processing lookup or 404 for id %s ...", product_id)
        return cls.query.get_or_404(product_id)

    @classmethod
    def find_by_user_id(cls, user_id):
        """Returns all Products with the user id

        Args:
            user_id (string): the user_id of the Products you want to match
        """
        logger.info("Processing user_id query for %s ...", user_id)
        return cls.query.filter(cls.user_id == user_id)

    @classmethod
    def find_product(cls, user_id, max_price, min_price):
        """Returns all Products with the given query parameter

        Args:
            max_price (float): the highest price you want to query
            min_price (float): the lowest price you want to query
        """
        query_info = f"user id: {user_id}"
        query_info += f"max price: {max_price} "
        query_info += f"min price: {min_price}"
        logger.info("Processing product query for %s ...", query_info)
        return cls.query.filter(and_(cls.user_id == user_id,
                                cls.price <= max_price, cls.price >= min_price))
    
    
