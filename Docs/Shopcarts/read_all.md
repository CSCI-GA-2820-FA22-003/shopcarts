
## Read all shopcarts
----
  Read all shopcarts in table

* **URL**

  GET /shopcarts

* **Request Headers:**
NULL
* **Body:**
NULL
 
* **Success Response:**
* **Code:** HTTP_200_OK <br />
    **Content:** 
    ```json
    [
        {
            "id": 3,
            "products": [
                {
                    "id": 2,
                    "name": "xixi",
                    "price": 2.0,
                    "product_id": "2",
                    "quantity": 13.0,
                    "time": "2020-12-13",
                    "user_id": "1"
                }
            ],
            "user_id": "1"
        }
    ]
    ```

* **Error Response:**
NULL