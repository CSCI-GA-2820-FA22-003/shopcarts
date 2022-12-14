"""
My Service

Describe what your service does here
"""
# pylint: disable=cyclic-import
import secrets
from functools import wraps
from flask import jsonify, request, abort
from flask_restx import fields, reqparse, Resource
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

product_model = api.model('Product', {
    'user_id': fields.String(required=True, description='The user_id of the product who buy it'),
    'product_id': fields.String(required=True, description='The id of the product'),
    'quantity': fields.Float(required=True, description='The quantity of products in shopcart'),
    'name': fields.String(required=True, description='The name of the Product'),
    'price': fields.Float(required=True, description='The price of the product'),
    'time': fields.Date(required=True, description='The day the record was created')
})

record_model = api.inherit(
    'RecordModel',
    product_model,
    {
        'id': fields.Integer(readOnly=True, description='The unique id assigned internally by service'),
    }
)

product_field = fields.Raw()
shopcart_model = api.model('Shopcart', {

    'user_id': fields.String(required=True, description='The user who own this shopcart'),
})

id_shopcart_model = api.inherit(
    'IdShopcartModel',
    shopcart_model,
    {
        'id': fields.Integer(readOnly=True, description='The unique id assigned internally by service'),
        'products': fields.List(cls_or_instance=product_field, required=False, description='The products it have')
    }
)

# query string arguments
product_args = reqparse.RequestParser()

product_args.add_argument('max-price', type=str, required=True, help='List products by max-price', location='args')
product_args.add_argument('min-price', type=str, required=True, help='List products by min-price', location='args')
product_args.add_argument('order-type', type=str, required=True, help='List product by order type', location='args')


######################################################################
# Authorization Decorator
######################################################################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-Api-Key' in request.headers:
            token = request.headers['X-Api-Key']
        if app.config.get('API_KEY') or app.config['API_KEY'] == token:
            return f(*args, **kwargs)
        return {'message': 'Invalid or missing token'}, 401
    return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """ Helper function used when testing API keys """
    return secrets.token_hex(16)


######################################################################
#  PATH: /shopcarts/{user_id}
######################################################################
@api.route('/shopcarts/<user_id>')
@api.param('user_id', 'The shopcart identifier')
class ShopcartResource(Resource):
    """
    ShopcartResource class

    Allows the manipulation of a single shopcart
    GET /shopcart{user_id} - Returns a shopcart with the user id
    PUT /shopcart{user_id} - Update a shopcart with the user id
    DELETE /shopcart{user_id} -  Deletes a shopcart with the user id
    """

    ######################################################################
    # READ A SHOPCART
    ######################################################################
    @api.doc('get_shopcart')
    @api.response(404, 'Shopcart not found')
    @api.marshal_with(id_shopcart_model)
    def get(self, user_id):
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
        return shopcarts[0].serialize(), status.HTTP_200_OK

    ######################################################################
    # UPDATE A SHOPCART
    ######################################################################
    @api.doc('update_shopcart', security='apikey')
    @api.response(404, 'Shopcart not found')
    @api.response(400, 'The posted Shopcart data was not valid')
    @api.expect(shopcart_model)
    @api.marshal_with(shopcart_model)
    @token_required
    def put(self, user_id):
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
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart {user_id} was not found.")

        shopcart = shopcarts[0]

        for product in shopcart.products:
            product.delete()

        for req in api.payload:
            # Create a product
            product = Products()
            product.deserialize(req)
            product.create()

        return shopcart.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A SHOPCART
    ######################################################################
    @api.doc('delete_shopcart', security='apikey')
    @api.response(404, 'Shopcart not found')
    @api.response(204, 'Shopcart deleted')
    @token_required
    def delete(self, user_id):
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
#  PATH: /shopcarts
######################################################################
@api.route('/shopcarts', strict_slashes=False)
class ShopcartCollection(Resource):
    """
    ShopcartCollection class

    Allows the manipulation of a single shopcart
    POST /shopcart - Create a shopcart
    GET /shopcart - Returns all shopcarts
    """

    #######################################################################
    # CREATE A SHOPCART
    #######################################################################

    @api.doc('create_shopcart', security='apikey')
    @api.response(400, 'The posted data was not valid')
    @api.expect(shopcart_model)
    @api.marshal_with(id_shopcart_model, code=201)
    @token_required
    def post(self):
        """Creates a new shopcart and stores it in the database
        Args:
            shopcart_model
        Returns:
            dict: the shopcart and it's value
        """
        app.logger.info("Request to Create shopcart")
        check_content_type("application/json")

        # See if the shopcart already exists and send an error if it does
        shopcart = Shopcarts()
        shopcart.deserialize(api.payload)     # check the fields are correct
        user_id = api.payload["user_id"]
        shopcart = Shopcarts.find_by_user_id(user_id)
        if len(shopcart.all()) != 0:
            abort(status.HTTP_409_CONFLICT, f"Shopcart {user_id} already exists")

        # Create the new shopcart
        shopcart = Shopcarts(user_id=user_id)
        shopcart.create()
        # Set the location header and return the new shopcart
        location_url = api.url_for(ShopcartResource, user_id=user_id, _external=True)
        return (
            shopcart.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )

    ######################################################################
    # LIST ALL SHOPCARTS
    ######################################################################

    @api.doc('get_all_shopcartS')
    @api.response(404, 'Shopcart not found')
    @api.marshal_with(id_shopcart_model)
    def get(self):
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
        return results, status.HTTP_200_OK


######################################################################
#  PATH: /shopcart/{user_id}/items/{product_id}
######################################################################
@api.route('/shopcarts/<user_id>/items/<product_id>')
@api.param('user_id', 'The shopcart identifier')
@api.param('product_id', 'The product_id identifier')
class ProductResource(Resource):
    """
    ProductResource class

    Allows the manipulation of a single shopcart
    GET /shopcart/{user_id}/items/{product_id} - Returns a product with the user id and product id
    PUT /shopcart/{user_id}/items/{product_id} - Update a product with the user id and product id
    DELETE /shopcart/{user_id}/items/{product_id} -  Deletes a product with the user id and product id
    """

    ######################################################################
    # READ A Product
    ######################################################################
    @api.doc('get_product')
    @api.response(404, 'Product not found')
    @api.marshal_with(product_model)
    def get(self, user_id, product_id):
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
            abort(status.HTTP_404_NOT_FOUND, f"Product with id {product_id} was not found in shopcart {user_id}.")

        # Return the new shopcart
        app.logger.info("Returning product: %s", product_id)
        return products[0].serialize(), status.HTTP_200_OK

    ######################################################################
    # UPDATE A Product
    ######################################################################
    @api.doc('update_product', security='apikey')
    @api.response(404, 'Product not found')
    @api.response(400, 'The posted Product data was not valid')
    @api.expect(product_model)
    @api.marshal_with(product_model)
    @token_required
    def put(self, user_id, product_id):
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
            abort(status.HTTP_404_NOT_FOUND, f"Product with id {product_id} was not found in shopcart {user_id}.")

        # Return the list of products
        app.logger.info("Updating product")
        originial_id = products[0].id
        product = products[0]
        product.deserialize(api.payload)
        product.id = originial_id
        product.update()

        app.logger.info("Product %s in shopcart %s was updated.", product_id, user_id)
        return product.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A Product
    ######################################################################
    @api.doc('delete_product', security='apikey')
    @api.response(404, 'Product not found')
    @api.response(204, 'Product deleted')
    @token_required
    def delete(self, user_id, product_id):
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
#  PATH: /shopcart/{user_id}/items
######################################################################
@api.route('/shopcarts/<user_id>/items', strict_slashes=False)
@api.param('user_id', 'The shopcart identifier')
class ItemsResource(Resource):
    """
    ItemsResource class

    Allows the manipulation of a single shopcart
    GET /shopcart{user_id} - Get all products with the user id
    POST /shopcart{user_id} - Add a product with the user id
    """
    ######################################################################
    # READ A Product
    ######################################################################
    @api.doc('get_product')
    # @api.response(404, 'Product not found')
    @api.expect(product_args, validate=True)
    @api.marshal_with(record_model)
    def get(self, user_id):
        """Read all products in the shopcart
        Args:
            user_id (str): the user_id of the shopcart
        Returns:
            list: the list of products in the shopcart
        """
        shopcarts = Shopcarts.find_by_user_id(user_id).all()
        if len(shopcarts) == 0:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart with id '{user_id}' was not found.")
        app.logger.info(f"Read products in the shopcart {user_id}")

        try:
            args = request.args
            if args.get('max-price') or args.get('max-price'):
                if args.get('max-price'):
                    max_price = args.get('max-price')
                    app.logger.info(f"Have max-price {max_price}")
                if args.get('min-price'):
                    min_price = args.get('min-price')
                    app.logger.info(f"Have min-price {min_price}")
                products = Products.find_product_with_range(user_id, max_price, min_price).all()
            elif args.get('order-type'):
                order_type = args.get('order-type')
                app.logger.info(f"Have order-type {order_type}")
                products = Products.find_product_with_order(user_id, order_type).all()
            else:
                max_price = args.get('max-price')
                min_price = args.get('min-price')
                products = Products.find_product_with_range(user_id, max_price, min_price).all()
                order_type = args.get('order-type')
                products = Products.find_product_with_order(user_id, order_type).all()
        except Exception as e:
            app.logger.info(e)
            products = Products.find_product(user_id).all()

        # Return the list of products
        app.logger.info("Returning products")
        serialized_products = []
        for product in products:
            serialized_products.append(product.serialize())
        return serialized_products, status.HTTP_200_OK

    ######################################################################
    # Add A Product
    ######################################################################
    @api.doc('add_product', security='apikey')
    @api.response(400, 'The posted data was not valid')
    @api.expect(product_model)
    @api.marshal_with(record_model, code=201)
    @token_required
    def post(self, user_id):
        """
        Add a product to the shopcart
        Args:
            user_id (str): the user_id of the shopcart
        Returns:
            dict: the added product
        """
        app.logger.info("Add a product into the shopcart")
        product = Products()
        check_content_type("application/json")
        product.deserialize(api.payload)
        shopcarts = Shopcarts.find_by_user_id(product.user_id).all()
        if len(shopcarts) == 0:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart {product.user_id} does not exist")
        product.create()
        app.logger.info(f"Product {product.product_id} created in shopcart {user_id}")

        # Set the location header and return the new product
        location_url = api.url_for(ProductResource, user_id=user_id, product_id=product.product_id, _external=True)
        return (
            product.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  PATH: /shopcart/{user_id}/empty
######################################################################
@api.route('/shopcarts/<user_id>/empty')
@api.param('user_id', 'The shopcart identifier')
class EmptyResource(Resource):
    """
    EmptyResource class

    Allows the manipulation of a single shopcart
    PUT /shopcart/{user_id}/empty - Empty a shopcart with the user id
    """
    ######################################################################
    # Empty A Shopcart
    ######################################################################
    @api.doc('empty_a_shopcart')
    @api.response(404, 'User_id not found')
    def put(self, user_id):
        """Empty a shopcart
        Args:
            user_id (str): the user_id of the shopcart
        Returns:
            dict: the emptied shopcart
        """
        app.logger.info(f"Request to Reset shopcart {user_id}...")

        # Get the current shopcart
        shopcarts = Shopcarts.find_by_user_id(user_id).all()
        if len(shopcarts) == 0:
            abort(status.HTTP_404_NOT_FOUND, f"Shopcart {user_id} does not exist")

        # empty the shopcart
        shopcart = shopcarts[0]
        shopcart.empty()

        return shopcart.serialize()


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
