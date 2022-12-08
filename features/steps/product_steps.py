import requests
from behave import given
from compare import expect
from service import app, routes
# api_key = routes.generate_apikey()
# app.config['API_KEY'] = api_key
headers = {'X-Api-Key': app.config['API_KEY']}

@given('the following shopcarts')
def step_impl(context):
    """ Delete all Shopcarts and load new ones """
    # List all of the shopcarts and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/api/shopcarts"

    context.resp = requests.get(rest_endpoint, headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for shopcart in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{shopcart['user_id']}", headers = headers)
        expect(context.resp.status_code).to_equal(204)

    # load the database with new shopcarts
    created = set()
    for row in context.table:
        user_id = row['user_id']
        if user_id not in created:
            created.add(user_id)
            payload = {
                "user_id": user_id
            }
            context.resp = requests.post(rest_endpoint, json=payload, headers=headers)
            expect(context.resp.status_code).to_equal(201)
    for row in context.table:
        payload = {
            "user_id": row['user_id'],
            "product_id": row['product_id'],
            "name": row['name'],
            "quantity": row['quantity'],
            "price": row['price'],
            "time": row['time']
        }
        app_endpoint = f"{context.BASE_URL}/shopcarts"
        product_endpoint = app_endpoint + f"/{row['user_id']}/items"
        context.resp = requests.post(product_endpoint, json=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
        