"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from .common import status  # HTTP Status Codes
from service.models import Products, Shopcarts
# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Welcome to the Shopcarts service",
        status.HTTP_200_OK,
    )

#######################################################################
# REST API
#######################################################################

#######################################################################
# Create shopcarts
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
# Read a shopcart
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
    """Returns all of the Shopcarts"""
    app.logger.info("Request for shopcart list")
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

    return jsonify(shopcart.serialize()),status.HTTP_201_CREATED

######################################################################
# ADD A PRODUCT
######################################################################
@app.route("/shopcarts/<user_id>/items", methods=["POST"])
def add_a_product(user_id):
    """Add a product to the shopcart"""
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
    """Read a product in the shopcart"""
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
    """Read all products in the shopcart"""
    shopcarts = Shopcarts.find_by_user_id(user_id).all()
    if len(shopcarts) == 0:
        abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{user_id}' was not found.")
    app.logger.info(f"Read all products in the shopcart {user_id}")
    products = Products.find_by_user_id(user_id).all()

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
    """Update a product in the shopcart"""
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
