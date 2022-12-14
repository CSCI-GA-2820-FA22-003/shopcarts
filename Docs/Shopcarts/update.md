
## Update shopcart
----
  Update a shopcart by user_id and shopcart list

* **URL**

  PUT /shopcarts/<user_id>

* **Request Headers:**
Content-Type: application/json
* **Body:**

  ```json
  [{
      "user_id": "1",
      "product_id": "2",
      "name": "xixi",
      "quantity": 133,
      "price": 2,
      "time": "2020-12-13"
  }]
  ```
 
* **Success Response:**

  * **Code:** HTTP_201_CREATED <br />
    **Content:** 
    ```json
    {
        "id": 3,
        "products": [
            {
                "id": 4,
                "name": "xixi",
                "price": 2.0,
                "product_id": "2",
                "quantity": 133.0,
                "time": "2020-12-13",
                "user_id": "1"
            }
        ],
        "user_id": "1"
    }
    ```

* **Error Response:**

  * **Code:** HTTP_409_CONFLICT <br />
    **Content:** 
    ```json
    {
    "error": "Conflict",
    "message": "409 Conflict: Shopcart 1 already exists",
    "status": 409
    }
    ```
