## Read a product
  Read a shopcart by user_id and product_id

* **URL**

  GET /shopcarts/<user_id>/items/<product_id>

* **Request Headers:**
NULL
* **Body:**
NULL
 
* **Success Response:**

  * **Code:** HTTP_200_OK <br />
    **Content:** 
    ```json
    {
        "id": 2,
        "name": "xixi",
        "price": 2.0,
        "product_id": "2",
        "quantity": 13.0,
        "time": "2020-12-13",
        "user_id": "1"
    }
    ```

* **Error Response:**

  * **Code:** HTTP_404_NOT_FOUND <br />
    **Content:** 
    ```json
    {
        "error": "Not Found",
        "message": "404 Not Found: Product with id 1 was not found in shopcart 1.",
        "status": 404
    }
    ```
