
## Create a shopcart
----
  Create a shopcart by user_id

* **URL**

  POST /shopcarts

* **Request Headers:**
Content-Type: application/json
* **Body:**

  ```json
  {
    "user_id": "1"
  }
  ```
 
* **Success Response:**

  * **Code:** HTTP_201_CREATED <br />
    **Content:** 
    ```json
    { 
      "id" : 1, 
      "name" : [], 
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
