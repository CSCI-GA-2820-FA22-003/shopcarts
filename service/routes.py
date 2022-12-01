"""
My Service

Describe what your service does here
"""
# pylint: disable=cyclic-import
import secrets
from functools import wraps
from flask import jsonify, request, url_for, abort
from flask_restx import fields, reqparse
from service.models import Products, Shopcarts
from .common import status  # HTTP Status Codes
# Import Flask application
from . import app, api


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
shopcart_model = api.model('Shopcart', {
    'id': fields.String(required=True, description='The id of Shopcart'),
    'user_id': fields.String(required=True, description='The user who own this shopcart'),
})

product_model = api.model('Product', {
    'id': fields.Integer(required=True, description='The id of the record'),
    'user_id': fields.String(required=True, description='The user_id of the product who buy it'),
    'product_id': fields.String(required=True, description='The id of the product'),
    'quantity': fields.Float(required=True, description='The quantity of products in shopcart'),
    'name': fields.String(required=True, description='The name of the Product'),
    'price': fields.Float(required=True, description='The price of the product'),
    'time': fields.Date(required=True, description='The day the record was created')
})

# query string arguments
product_args = reqparse.RequestParser()
product_args.add_argument('user_id', type=str, required=False, help='List records by user_id')
product_args.add_argument('product_id', type=str, required=False, help='List records by category')
product_args.add_argument('name', type=str, required=False, help='List Pets by availability')


######################################################################
# Authorization Decorator
######################################################################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-Api-Key' in request.headers:
            token = request.headers['X-Api-Key']

        if app.config.get('API_KEY') and app.config['API_KEY'] == token:
            return f(*args, **kwargs)
        else:
            return {'message': 'Invalid or missing token'}, 401
    return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """ Helper function used when testing API keys """
    return secrets.token_hex(16)


#######################################################################
# REST API
#######################################################################

#######################################################################
# CREATE A SHOPCART
#######################################################################


@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """Creates a new shopcart and stores it in the database
    Args:
        user_id (str): the user_id of the shopcart to create
    Returns:
        dict: the shopcart and it's value
    """
    app.logger.info("Request to Create shopcart")
    check_content_type("application/json")

    # See if the shopcart already exists and send an error if it does
    shopcart = Shopcarts()
    shopcart.deserialize(request.get_json())     # check the fields are correct
    user_id = request.get_json()["user_id"]
    shopcart = Shopcarts.find_by_user_id(user_id)
    if len(shopcart.all()) != 0:
        abort(status.HTTP_409_CONFLICT, f"Shopcart {user_id} already exists")

    # Create the new shopcart
    shopcart = Shopcarts(user_id=user_id)
    shopcart.create()

    # Set the location header and return the new shopcart
    location_url = url_for("read_a_shopcart", user_id=user_id, _external=True)
    return (
        jsonify(shopcart.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )

######################################################################
# READ A SHOPCART
######################################################################


@app.route("/shopcarts/<user_id>", methods=["GET"])
def read_a_shopcart(user_id):
    """Read a shopcart
    Args:
        user_id (str): the user_id of the shopcart to create
    Returns:
        dict: the shopcart and it's value
    """
    app.logger.info(f"Request to Read shopcart {user_id}...")

    # See if the shopcart already exists and send an error if it does
    shopcarts = Shopcarts.find_by_user_id(user_id).all()
    if len(shopcarts) == 0:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{user_id}' was not found.")

    # Return the new shopcart
    app.logger.info("Returning shopcart: %s", user_id)
    return jsonify(shopcarts[0].serialize()), status.HTTP_200_OK

######################################################################
# LIST ALL SHOPCARTS
######################################################################


@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """List all shopcarts
    Returns:
        list: the list of all shopcarts and their contents
    """
    app.logger.info("Request for shopcart list")
    args = request.args
    user_id = args.get("user-id", default="", type=str)
    if user_id:
        shopcarts = []
        shopcarts = Shopcarts.find_by_user_id(user_id).all()
    else:
        shopcarts = []
        shopcarts = Shopcarts.all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    app.logger.info("Returning %d shopcarts", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# UPDATE A SHOPCART
######################################################################
@app.route("/shopcarts/<user_id>", methods=["PUT"])
def update_a_shopcart(user_id):
    """Update items in shopcart
    Args:
        user_id (str): the user_id of the shopcart to update
    Returns:
        dict: the shopcart and it's value
    """

    app.logger.info(f"Request to update a shopcart for {user_id}")
    check_content_type("application/json")
    shopcarts = Shopcarts.find_by_user_id(user_id).all()

    if len(shopcarts) == 0:
        abort(status.HTTP_404_NOT_FOUND,
              f"Shopcart {user_id} was not found.")

    shopcart = shopcarts[0]

    for product in shopcart.products:
        product.delete()

    for req in request.get_json():
        # Create a product
        product = Products()
        product.deserialize(req)
        product.create()

    return jsonify(shopcart.serialize()), status.HTTP_200_OK

######################################################################
# DELETE A SHOPCART
######################################################################


@app.route("/shopcarts/<user_id>", methods=["DELETE"])
def delete_a_shopcart(user_id):
    """Deletes a shopcart
    Args:
        user_id (str): the user_id of the shopcart to delete
    Returns:
        str: always returns an empty string
    """
    app.logger.info(f"Request to Delete shopcart {user_id}...")

    shopcarts = Shopcarts.find_by_user_id(user_id).all()
    if len(shopcarts) != 0:
        for shopcart in shopcarts:
            shopcart.delete()

    # Return nothing but 204 status code
    app.logger.info("Shopcart %s delete complete", user_id)
    return "", status.HTTP_204_NO_CONTENT

######################################################################
# ADD A PRODUCT
######################################################################


@app.route("/shopcarts/<user_id>/items", methods=["POST"])
def add_a_product(user_id):
    """Add a product to the shopcart
    Args:
        user_id (str): the user_id of the shopcart
    Returns:
        dict: the added product
    """
    app.logger.info("Add a product into the shopcart")
    product = Products()
    check_content_type("application/json")
    product.deserialize(request.get_json())
    product.create()
    app.logger.info(f"Product {product.product_id} created in shopcart {user_id}")

    # Set the location header and return the new product
    location_url = url_for("read_a_product", user_id=user_id,
                           product_id=product.product_id, _external=True)
    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )

######################################################################
# READ A PRODUCT
######################################################################


@app.route("/shopcarts/<user_id>/items/<product_id>", methods=["GET"])
def read_a_product(user_id, product_id):
    """Read a product in the shopcart
    Args:
        user_id (str): the user_id of the shopcart
        product_id (str): the product_id of the product
    Returns:
        dict: the product
    """
    app.logger.info(f"Read a product {product_id} in the shopcart {user_id}")
    products = Products.find_by_user_id_product_id(user_id, product_id).all()

    if len(products) == 0:
        abort(status.HTTP_404_NOT_FOUND,
              f"Product with id {product_id} was not found in shopcart {user_id}.")

    # Return the new shopcart
    app.logger.info("Returning product: %s", product_id)
    return jsonify(products[0].serialize()), status.HTTP_200_OK

######################################################################
# LIST ALL PRODUCTS
######################################################################


@app.route("/shopcarts/<user_id>/items", methods=["GET"])
def list_all_products(user_id):
    """Read all products in the shopcart
    Args:
        user_id (str): the user_id of the shopcart
    Returns:
        list: the list of products in the shopcart
    """
    args = request.args
    max_price = args.get("max-price", default=float('inf'), type=float)
    min_price = args.get("min-price", default=-float('inf'), type=float)
    shopcarts = Shopcarts.find_by_user_id(user_id).all()
    if len(shopcarts) == 0:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{user_id}' was not found.")
    app.logger.info(f"Read all products in the shopcart {user_id}")
    products = Products.find_product(user_id, max_price, min_price).all()

    # Return the list of products
    app.logger.info("Returning products")
    serialized_products = []
    for product in products:
        serialized_products.append(product.serialize())
    return jsonify(serialized_products), status.HTTP_200_OK

######################################################################
# UPDATE A PRODUCT
######################################################################


@app.route("/shopcarts/<user_id>/items/<product_id>", methods=["PUT"])
def update_a_product(user_id, product_id):
    """Update a product in the shopcart
    Args:
        user_id (str): the user_id of the shopcart
        product_id (str): the product_id of the product
    Returns:
        dict: the product
    """
    app.logger.info(f"Read a product {product_id} in the shopcart {user_id}")
    products = Products.find_by_user_id_product_id(user_id, product_id).all()

    if len(products) == 0:
        abort(status.HTTP_404_NOT_FOUND,
              f"Product with id {product_id} was not found in shopcart {user_id}.")

    # Return the list of products
    app.logger.info("Updating product")
    originial_id = products[0].id
    product = products[0]
    product.deserialize(request.get_json())
    product.id = originial_id
    product.update()

    app.logger.info("Product %s in shopcart %s was updated.", product_id, user_id)
    return jsonify(product.serialize()), status.HTTP_200_OK

######################################################################
# DELETE A PRODUCT
######################################################################


@app.route("/shopcarts/<user_id>/items/<product_id>", methods=["DELETE"])
def delete_a_product(user_id, product_id):
    """Update a product in the shopcart
    Args:
        user_id (str): the user_id of the shopcart
        product_id (str): the product_id of the product
    Returns:
        str: always returns an empty string
    """
    app.logger.info(f"Delete a product {product_id} in the shopcart {user_id}")
    products = Products.find_by_user_id_product_id(user_id, product_id).all()

    app.logger.info("Deleting product")
    if len(products) != 0:
        # Return the list of products
        product = products[0]
        product.delete()

    app.logger.info("Product %s in shopcart %s was deleted.", product_id, user_id)
    return "", status.HTTP_204_NO_CONTENT

######################################################################
# EMPTY A SHOPCART
######################################################################


@app.route("/shopcarts/<user_id>/empty", methods=["PUT"])
def empty_shopcarts(user_id):
    """Empty a shopcart
    Args:
        user_id (str): the user_id of the shopcart
    Returns:
        dict: the emptied shopcart
    """
    app.logger.info(f"Request to Reset shopcart {user_id}...")

    # Get the current shopcart
    shopcarts = Shopcarts.find_by_user_id(user_id).all()
    if shopcarts is None:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart {user_id} does not exist")

    # empty the shopcart
    shopcart = shopcarts[0]
    shopcart.empty()

    return jsonify(shopcart.serialize())

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
