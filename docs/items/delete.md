## Delete a product
  Delete a product by user_id and product_id

* **URL**

  DELETE /shopcarts/<user_id>/items/<product_id>

* **Request Headers:**
NULL
* **Body:**
NULL
 
* **Success Response:**

  * **Code:** HTTP_204_NO_CONTENT <br />
    **Content:** 
    NO_CONTENT

* **Error Response:**

  * **Code:** HTTP_404_NOT_FOUND <br />
    **Content:** 
    ```json
    {
        "error": "Not Found",
        "message": "404 Not Found: Product with id 3 was not found in shopcart 2.",
        "status": 404
    }
    ```
