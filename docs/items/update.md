## Update a product
  Update a product by user_id and product_id and product detail

* **URL**

  PUT /shopcarts/<user_id>/items/<product_id>

* **Request Headers:**
Content-Type: application/json
* **Body:**

  ```json
  {
      "user_id": "1",
      "product_id": "2",
      "name": "xixi",
      "quantity": 131,
      "price": 2,
      "time": "2020-12-13"
  }
  ```
 
* **Success Response:**

  * **Code:** HTTP_200_OK <br />
    **Content:** 
    ```
    {
        "id": 2,
        "name": "xixi",
        "price": 2.0,
        "product_id": "2",
        "quantity": 131.0,
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
        "message": "404 Not Found: Product with id 21 was not found in shopcart 1.",
        "status": 404
    }
    ```
