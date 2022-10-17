# This is the project for our shopcarts team

## Important: Before you submit a pull request. Make sure

- Run `nosetests` to make sure that all tests are passed and code coverage are no less than 95%

- Run `make lint` to make sure that there is no Pylint error. 

## Reminder: Whenever you make changes to the table schema. Run `flask create-db` to sync the database

## Run `flask run` to start the service. If you want to clean the database, run `flask create-db`.

Product table schema
```
{
      id: auto_generated       Int         Primary key
      user_id: user_id1          String       foreign key
      product_id: product_id1         String        key
      quantity: product_quantity1        Float
      name: product_name1       String
      price: price1             Float
      time: purchase_time1         Date
}
```
Shopcarts table schema
```
Shopcarts schema
{
      id: auto_generated       Int         Primary key
      user_id: user_id1          String       unique
}
```
