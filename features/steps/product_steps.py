import requests
from behave import given
from compare import expect


@given('the following shopcarts')
def step_impl(context):
    """ Delete all Shopcarts and load new ones """
    # List all of the pets and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/shopcarts"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for shopcart in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{shopcart['user_id']}")
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
            context.resp = requests.post(rest_endpoint, json=payload)
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
        product_endpoint = rest_endpoint + f"/{row['user_id']}/items"
        context.resp = requests.post(product_endpoint, json=payload)
        expect(context.resp.status_code).to_equal(201)
        