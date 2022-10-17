# This is the project for our shopcarts team

## Reminder: Whenever you make changes to the table schema. Run `flask create-db` to sync the database

## Run `flask run` to start the service. If you want to clean the database, run `flask create-db`.

Product table schema
```
{
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
      user_id: user_id1          String       unique
}
```
