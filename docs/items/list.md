## Read all product
  Read all products in a shopcart

* **URL**

  GET /shopcarts/<user_id>/items

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
            "id": 2,
            "name": "xixi",
            "price": 2.0,
            "product_id": "2",
            "quantity": 13.0,
            "time": "2020-12-13",
            "user_id": "1"
        },
        {
            "id": 3,
            "name": "haha",
            "price": 1.0,
            "product_id": "3",
            "quantity": 12.0,
            "time": "2020-12-12",
            "user_id": "1"
        }
    ]
    ```

* **Error Response:**

  * **Code:** HTTP_404_NOT_FOUND <br />
    **Content:** 
    ```json
    {
        "error": "Not Found",
        "message": "404 Not Found: Shopcart with id '11' was not found.",
        "status": 404
    }
    ```
