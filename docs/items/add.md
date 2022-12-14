## Create a product
  Create a product by used_id and product detail

* **URL**

  POST /shopcarts/<user_id>/items

* **Request Headers:**
Content-Type: application/json
* **Body:**

  ```json
  {
      "user_id": "1",
      "product_id": "2",
      "name": "haha",
      "quantity": 12,
      "price": 1,
      "time": "2020-12-12"
  }
  ```
 
* **Success Response:**

  * **Code:** HTTP_201_CREATED <br />
    **Content:** 
      ```json
      {
          "id": 1,
          "name": "haha",
          "price": 1.0,
          "product_id": "2",
          "quantity": 12.0,
          "time": "2020-12-12",
          "user_id": "1"
      }
      ```

* **Error Response:**
NULL
