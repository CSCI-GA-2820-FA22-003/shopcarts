Feature: The shopcart service back-end
    As a User
    I need a Shopcart service
    So that I can keep track of all my products in the shopcart

Background:
    Given the following shopcarts
        | user_id | product_id | name | quantity | price | time       |
        | 1       | 3          | pen  | 1        | 2     | 2019-11-18 |
        | 1       | 4          | food | 2        | 4     | 2019-11-18 |
        | 1       | 5          | water| 3        | 6     | 2019-11-18 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Shopcart
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "User ID" to "2"
    And I press the "Create Shopcart" button
    Then I should see the message "Create shopcart successfully"
    When I press the "Read this" button
    Then I should see the message "No items in current shopcart"

Scenario: Create a Product
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "User ID" to "1"
    And I set the "Product ID" to "6"
    And I set the "Name" to "test"
    And I set the "Quantity" to "2"
    And I set the "Price" to "5"
    And I set the "Time" to "11-29-2022"
    And I press the "Create" button
    Then I should see the message "Record has been created"
    When I press the "Read this" button
    Then I should see the message "Success"
    And I should see "pen" in the results
    And I should see "food" in the results
    And I should not see "pig" in the results
    And I should see "test" in the results
    When I press the "Clear" button
    And I set the "User ID" to "1"
    And I set the "Product ID" to "6"
    And I press the "Retrieve record" button
    Then I should see the message "Success"
    And I should see "test" in the results

Scenario: List all shopcarts
    When I visit the "Home Page"
    And I press the "List" button
    Then I should see the message "Success"
    And I should see "pen" in the results
    And I should see "food" in the results
    And I should not see "pig" in the results

Scenario: Update a product
    When I visit the "home page"
    And I press the "Clear" button
    And I set the "User ID" to "1"
    And I set the "Product ID" to "3"
    And I set the "Name" to "new_test"
    And I set the "Price" to "5"
    And I set the "Quantity" to "4"
    And I set the "Time" to "02-02-2023"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "List" button
    Then I should see "new_test" in the results
    Then I should not see "pen" in the results

Scenario: Delete a product
    When I visit the "home page"
    And I press the "Clear" button
    And I set the "User ID" to "1"
    And I set the "Product ID" to "3"
    And I press the "Delete record" button
    Then I should see the message "Item has been Deleted!"
    When I press the "List" button
    Then I should not see "pen" in the results

Scenario: Delete a shopcart
    When I visit the "home page"
    And I press the "Clear" button
    And I set the "User ID" to "1"
    And I press the "Delete" button
    Then I should see the message "Shopcart has been Deleted!"
    When I press the "List" button
    Then I should not see "pen" in the results
    Then I should not see "food" in the results
    Then I should not see "water" in the results
    When I press the "Clear" button
    And I set the "User ID" to "1"
    And I press the "Read this" button
    Then I should see the message "404 Not Found: Shopcart with id '1' was not found."

Scenario: Empty a shopcart
    When I visit the "home page"
    And I press the "Clear" button
    And I set the "User ID" to "1"
    And I press the "Empty" button
    Then I should see the message "Shopcart has been emptied!"
    When I press the "List" button
    Then I should not see "pen" in the results
    Then I should not see "food" in the results
    Then I should not see "water" in the results
    When I press the "Clear" button
    And I set the "User ID" to "1"
    And I press the "Read this" button
    Then I should see the message "No items in current shopcart"

Scenario: Query a product with max and min price
    When I visit the "home page"
    And I press the "Clear" button
    And I set the "User ID" to "1"
    And I set the "Max Price" to "5"
    And I set the "Min Price" to "3"
    And I press the "Query" button
    Then I should see the message "Success"
    Then I should not see "pen" in the results
    Then I should see "food" in the results
    Then I should not see "water" in the results
