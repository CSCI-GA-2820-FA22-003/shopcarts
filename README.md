# This is the project for our shopcarts team

[![Build Status](https://github.com/2022-DevOps-Shopcarts/shopcarts/actions/workflows/workflow.yml/badge.svg)](https://github.com/2022-DevOps-Shopcarts/shopcarts/actions)
[![BDD Tests](https://github.com/CSCI-GA-2820-FA22-003/shopcarts/actions/workflows/bdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA22-003/shopcarts/actions/workflows/bdd.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA22-003/shopcarts/branch/main/graph/badge.svg?token=7E17S7VS4E)](https://codecov.io/gh/CSCI-GA-2820-FA22-003/shopcarts)

## The service has been deployed to IBM clod

- The url is http://169.51.194.219/

- The development version of the app is on port 31001

- The production version of the app is on port 31002

## Important: Before you submit a pull request. Make sure

- Run `nosetests` to make sure that all tests are passed and code coverage are no less than 95%

- Run `make lint` to make sure that there is no Pylint error. 

- Run the tests using `behave`

  Start the server in a separate bash shell:

  ```sh
  honcho start
  ```

  Then start behave in your original bash shell:

  ```sh
  behave
  ```
## Reminder: Whenever you make changes to the table schema. Run `flask create-db` to sync the database

## Run `flask run` to start the service. If you want to clean the database, run `flask create-db`.

## Run `honcho start` to start the User Interface service.

Product table schema
```
{
      id: auto_generated            Int           Primary key
      user_id: user_id1             String        foreign key
      product_id: product_id1       String        key
      quantity: product_quantity1   Float
      name: product_name1           String
      price: price1                 Float
      time: purchase_time1          Date
}
```
Shopcarts table schema
```
Shopcarts schema
{
      id: auto_generated          Int          Primary key
      user_id: user_id1           String       unique
}
```

**List of REST API endpoints**
----

POST   /shopcarts: [Create a shopcart](./docs/shopcarts/create.md)\
GET    /shopcarts: [List all shopcarts](./docs/shopcarts/read_all.md)\
GET    /shopcarts/{id}: [Read a shopcart](./docs/shopcarts/read.md)\
PUT    /shopcarts/{id}: [Update a shopcart](./docs/shopcarts/update.md)\
DELETE /shopcarts/{id}: [Delete a shopcart](./docs/shopcarts/delete.md)

POST   /shopcarts/{id}/items: [Add an item to a shopcart](./docs/items/add.md)\
GET    /shopcarts/{id}/items: [List all items in a shopcart](./docs/items/list.md)\
GET    /shopcarts/{id}/items/{id}: [Read an item from a shopcart](./docs/items/read.md)\
PUT    /shopcarts/{id}/items/{id}: [Update an item in a shopcart](./docs/items/update.md)\
DELETE /shopcarts/{id}/items/{id}: [Delete an item from a shopcart](./docs/items/delete.md)
