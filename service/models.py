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


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Shopcarts(db.Model):
    """
    Class that represents a Products
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(63), nullable=False, unique=True)

class Products(db.Model):
    """
    Class that represents a Products
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(63), db.ForeignKey("shopcarts.userId"), nullable=False)
    productId = db.Column(db.String(63), nullable=False)
    name = db.Column(db.String(63), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    time = db.Column(db.Date, nullable=False, default=date.today())

    def __repr__(self):
        return "<Products %s in user %s's shopcart>" % (self.name, self.userId)

    def create(self):
        """
        Creates a Products to the database
        """
        logger.info("Creating %s", self.name)
        products = self.find_by_user_id_product_id(self.userId, self.productId)
        if len(products.all()) > 0:
            self.id = products.all()[0].id
            db.session.commit()
        else:
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
            "userId": self.userId,
            "productId": self.productId,
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
            self.userId = data["userId"]
            self.productId = data["productId"]
            self.name = data["name"]
            self.quantity = data["quantity"]
            self.price = data["price"]
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
        logger.info("Processing userId and productId query for %s and %s ..." 
        % (user_id, product_id))
        return cls.query.filter(
            and_(
                cls.userId == user_id,
                cls.productId == product_id
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
