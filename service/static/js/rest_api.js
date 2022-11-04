$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        
        $("#product_id").val(res.id);
        $("#product_name").val(res.name);
        $("#user_id").val(res.user_id);
        $("#quantity").val(res.quantity);
        $("#price").val(res.price);
        $("#record_time").val(res.time);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_name").val("");
        $("#user_id").val("");
        $("#product_id").val("");
        $("#quantity").val("");
        $("#price").val("");
        $("#record_time").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Record
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#product_name").val();
        let UserID = $("#user_id").val();
        let productID = $("#product_id").val();
        let quantity = $("#quantity").val();
        let price = $("#price").val();
        let recordTime = $("#record_time").val();
        
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
                flash_message("Success")
            });
    
            ajax.fail(function(res){
                flash_message(res.responseJSON.message)
            });
        }

    });


    // ****************************************
    // Update a Record
    // ****************************************

    $("#update-btn").click(function () {

        let name = $("#product_name").val();
        let UserID = $("#user_id").val();
        let productID = $("#product_id").val();
        let quantity = $("#quantity").val();
        let price = $("#price").val();
        let recordTime = $("#record_time").val();
        
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

    $("#new-cart-btn").click(function () {

        let user_id = $("#user_id").val();

        let data = {
            "user_id": user_id,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: `/shopcarts`,
            contentType: "application/json",
            data: JSON.stringify(data)
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

    });

    // ****************************************
    // Retrieve a Record
    // ****************************************

    $("#retrieve-btn").click(function () {

        let user_id = $("#user_id").val();
        let product_id = $("#product_id").val();

        $("#flash_message").empty();

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

    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        let user_id = $("#user_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${user_id}`,
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
    // Get all
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#product_name").val();
        let UserID = $("#user_id").val();
        let price = $("#price").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (UserID) {
            if (queryString.length > 0) {
                queryString += '&UserID=' + UserID
            } else {
                queryString += 'UserID=' + UserID
            }
        }
        if (price) {
            if (queryString.length > 0) {
                queryString += '&price=' + price
            } else {
                queryString += 'price=' + price
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/pets?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">UserID</th>'
            table += '<th class="col-md-2">price</th>'
            table += '<th class="col-md-2">quantity</th>'
            table += '<th class="col-md-2">recordTime</th>'
            table += '</tr></thead><tbody>'
            let firstPet = "";
            for(let i = 0; i < res.length; i++) {
                let pet = res[i];
                table +=  `<tr id="row_${i}"><td>${pet.id}</td><td>${pet.name}</td><td>${pet.UserID}</td><td>${pet.price}</td><td>${pet.quantity}</td><td>${pet.recordTime}</td></tr>`;
                if (i == 0) {
                    firstPet = pet;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPet != "") {
                update_form_data(firstPet)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#product_name").val();
        let UserID = $("#user_id").val();
        let price = $("#price").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (UserID) {
            if (queryString.length > 0) {
                queryString += '&UserID=' + UserID
            } else {
                queryString += 'UserID=' + UserID
            }
        }
        if (price) {
            if (queryString.length > 0) {
                queryString += '&price=' + price
            } else {
                queryString += 'price=' + price
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/pets?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">UserID</th>'
            table += '<th class="col-md-2">price</th>'
            table += '<th class="col-md-2">quantity</th>'
            table += '<th class="col-md-2">recordTime</th>'
            table += '</tr></thead><tbody>'
            let firstPet = "";
            for(let i = 0; i < res.length; i++) {
                let pet = res[i];
                table +=  `<tr id="row_${i}"><td>${pet.id}</td><td>${pet.name}</td><td>${pet.UserID}</td><td>${pet.price}</td><td>${pet.quantity}</td><td>${pet.recordTime}</td></tr>`;
                if (i == 0) {
                    firstPet = pet;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPet != "") {
                update_form_data(firstPet)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
