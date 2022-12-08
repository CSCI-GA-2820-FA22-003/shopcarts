$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    let PREFIX = "/api"
    // Updates the form with data from the response
    function update_form_data(res) {
        
        $("#product_id").val(res.product_id);
        $("#name").val(res.name);
        $("#user_id").val(res.user_id);
        $("#quantity").val(res.quantity);
        $("#price").val(res.price);
        $("#time").val(res.time);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#name").val("");
        $("#user_id").val("");
        $("#product_id").val("");
        $("#quantity").val("");
        $("#price").val("");
        $("#time").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Record / Add an item to a shopcart
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#name").val();
        let UserID = $("#user_id").val();
        let productID = $("#product_id").val();
        let quantity = $("#quantity").val();
        let price = $("#price").val();
        let recordTime = $("#time").val();
        
        let data = {
            "user_id": UserID,
            "product_id": productID,
            "name": name,
            "quantity": parseFloat(quantity),
            "price": parseFloat(price),
            "time": recordTime
        };

        $("#flash_message").empty();
        
        if(!UserID){
            flash_message("Please Input User ID")
        }else{
            let ajax = $.ajax({
                type: "POST",
                url: `/shopcarts/${UserID}/items`,
                contentType: "application/json",
                data: JSON.stringify(data),
            });
    
            ajax.done(function(res){
                update_form_data(res)
                flash_message("Record has been created")
            });
    
            ajax.fail(function(res){
                flash_message(res.responseJSON.message)
            });
        }

    });


    // ****************************************
    // Update a Record / Update an item in a shopcart
    // ****************************************

    $("#update-btn").click(function () {

        let name = $("#name").val();
        let UserID = $("#user_id").val();
        let productID = $("#product_id").val();
        let quantity = $("#quantity").val();
        let price = $("#price").val();
        let recordTime = $("#time").val();
        
        let data = {
            "user_id": UserID,
            "product_id": productID,
            "name": name,
            "quantity": parseFloat(quantity),
            "price": parseFloat(price),
            "time": recordTime
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/shopcarts/${UserID}/items/${productID}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Create a new shopcart
    // ****************************************

    $("#create-shopcart-btn").click(function () {

        let user_id = $("#user_id").val();

        let data = {
            "user_id": user_id,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: `${PREFIX}/shopcarts`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Create shopcart successfully")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // List all shopcarts
    // ****************************************

    $("#list-btn").click(function () {

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${PREFIX}/shopcarts`,
            contentType: "application/json"
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            if(res.length==0){
                flash_message("No shopcart")
            }else{
                
                let table = '<table class="table table-striped" cellpadding="10">'
                table += '<thead><tr>'
                table += '<th class="col-md-2">ProductID</th>'
                table += '<th class="col-md-2">Name</th>'
                table += '<th class="col-md-2">UserID</th>'
                table += '<th class="col-md-2">price</th>'
                table += '<th class="col-md-2">quantity</th>'
                table += '<th class="col-md-2">recordTime</th>'
                table += '</tr></thead><tbody>'
                let firstProduct = "";
                for(let j = 0; j < res.length; j++){
                    let shopcart = res[j];
                    let products = shopcart.products;
                    for(let i = 0; i < products.length; i++) {
                        let product = products[i];
                        table +=  `<tr id="row_${i}"><td>${product.product_id}</td><td>${product.name}</td><td>${product.user_id}</td><td>${product.price}</td><td>${product.quantity}</td><td>${product.time}</td></tr>`;
                        if (i == 0) {
                            firstProduct = product;
                        }
                    } 
                }
                table += '</tbody></table>';
                $("#search_results").append(table);
                
                flash_message("Success")
            }
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Record / Read an item from a shopcart
    // ****************************************

    $("#retrieve-record-btn").click(function () {

        let user_id = $("#user_id").val();
        let product_id = $("#product_id").val();

        $("#flash_message").empty();
        if(!user_id||!product_id){
            flash_message("Please fill userID and productID")
        }else{
            let ajax = $.ajax({
                type: "GET",
                url: `/shopcarts/${user_id}/items/${product_id}`,
                contentType: "application/json",
                data: ''
            })
    
            ajax.done(function(res){
                //alert(res.toSource())
                update_form_data(res)
                flash_message("Success")
            });
    
            ajax.fail(function(res){
                clear_form_data()
                flash_message(res.responseJSON.message)
            });
        }
    });

    // ****************************************
    //  Delete an item from a shopcart
    // ****************************************

    $("#delete-record-btn").click(function () {

        let user_id = $("#user_id").val();
        let product_id = $("#product_id").val();

        $("#flash_message").empty();
        if(!user_id||!product_id){
            flash_message("Please fill userID and productID")
        }else{
            let ajax = $.ajax({
                type: "DELETE",
                url: `/shopcarts/${user_id}/items/${product_id}`,
                contentType: "application/json",
                data: '',
            })

            ajax.done(function(res){
                clear_form_data()
                flash_message("Item has been Deleted!")
            });

            ajax.fail(function(res){
                flash_message("Server error!")
            });
        }
    });

    // ****************************************
    //  Delete a shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        let user_id = $("#user_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `${PREFIX}/shopcarts/${user_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Shopcart has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#user_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Read all products in a shopcart
    // ****************************************

    $("#read-this-btn").click(function () {

        let user_id = $("#user_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${user_id}/items`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            if(res.length==0){
                flash_message("No items in current shopcart")
            }else{
                let table = '<table class="table table-striped" cellpadding="10">'
                table += '<thead><tr>'
                table += '<th class="col-md-2">ProductID</th>'
                table += '<th class="col-md-2">Name</th>'
                table += '<th class="col-md-2">UserID</th>'
                table += '<th class="col-md-2">price</th>'
                table += '<th class="col-md-2">quantity</th>'
                table += '<th class="col-md-2">recordTime</th>'
                table += '</tr></thead><tbody>'
                let firstProduct = "";
                for(let i = 0; i < res.length; i++) {
                    let product = res[i];
                    table +=  `<tr id="row_${i}"><td>${product.product_id}</td><td>${product.name}</td><td>${product.user_id}</td><td>${product.price}</td><td>${product.quantity}</td><td>${product.time}</td></tr>`;
                    if (i == 0) {
                        firstProduct = product;
                    }
                }
                table += '</tbody></table>';
                $("#search_results").append(table);
                
                flash_message("Success")
            }
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    //  Empty a shopcart
    // ****************************************

    $("#empty-btn").click(function () {

        let user_id = $("#user_id").val();

        $("#flash_message").empty();
        if(!user_id){
            flash_message("Please fill userID")
        }else{
            let ajax = $.ajax({
                type: "PUT",
                url: `/shopcarts/${user_id}/empty`,
                contentType: "application/json",
                data: '',
            })

            ajax.done(function(res){
                clear_form_data()
                flash_message("Shopcart has been emptied!")
            });

            ajax.fail(function(res){
                flash_message("Server error!")
            });
        }
    });

    // ****************************************
    // Query products using max and min price
    // ****************************************

    $("#query-btn").click(function () {

        let user_id = $("#user_id").val();
        let max_price = $("#max_price").val();
        let min_price = $("#min_price").val();

        $("#flash_message").empty();
        if(!user_id||!max_price||!min_price){
            flash_message("Please fill userID and Max price and Min price")
        }else{
            let ajax = $.ajax({
                type: "GET",
                url: `/shopcarts/${user_id}/items?max-price=${max_price}&min-price=${min_price}`,
                contentType: "application/json",
                data: ''
            })
    
            ajax.done(function(res){
                //alert(res.toSource())
                $("#search_results").empty();
                let table = '<table class="table table-striped" cellpadding="10">'
                table += '<thead><tr>'
                table += '<th class="col-md-2">ProductID</th>'
                table += '<th class="col-md-2">Name</th>'
                table += '<th class="col-md-2">UserID</th>'
                table += '<th class="col-md-2">price</th>'
                table += '<th class="col-md-2">quantity</th>'
                table += '<th class="col-md-2">recordTime</th>'
                table += '</tr></thead><tbody>'
                let firstProduct = "";
                for(let i = 0; i < res.length; i++) {
                    let product = res[i];
                    table +=  `<tr id="row_${i}"><td>${product.product_id}</td><td>${product.name}</td><td>${product.user_id}</td><td>${product.price}</td><td>${product.quantity}</td><td>${product.time}</td></tr>`;
                    if (i == 0) {
                        firstProduct = product;
                    }
                }
                table += '</tbody></table>';
                $("#search_results").append(table);
                flash_message("Success")
            });
    
            ajax.fail(function(res){
                clear_form_data()
                flash_message(res.responseJSON.message)
            });
        }
    });

})
