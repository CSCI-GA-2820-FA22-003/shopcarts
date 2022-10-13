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


######################################################################
# REST API
######################################################################

# -----------------------------------------------------------
# Create shopcarts
# -----------------------------------------------------------
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """Creates a new counter and stores it in the database
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

    # Create the new counter
    shopcart = Shopcarts(user_id=user_id)
    shopcart.create()

    # Set the location header and return the new counter
    location_url = url_for("read_a_shopcart", user_id=user_id, _external=True)
    return (
        jsonify(shopcart.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )

# -----------------------------------------------------------
# Read a shopcart
# -----------------------------------------------------------
@app.route("/shopcarts/<user_id>", methods=["GET"])
def read_a_shopcart(user_id):
    """Creates a new counter and stores it in the database
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

    # Set the location header and return the new counter
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
