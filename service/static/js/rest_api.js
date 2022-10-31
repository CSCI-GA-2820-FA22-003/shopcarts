$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res.id);
        $("#product_name").val(res.name);
        $("#user_id").val(res.UserID);
        if (res.available == true) {
            $("#pet_available").val("true");
        } else {
            $("#pet_available").val("false");
        }
        $("#pet_gender").val(res.gender);
        $("#record_time").val(res.recordTime);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_name").val("");
        $("#user_id").val("");
        $("#pet_available").val("");
        $("#pet_gender").val("");
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


        // let available = $("#pet_available").val() == "true";
        // let gender = $("#pet_gender").val();
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
            type: "POST",
            url: "/shopcarts/"+UserID+"/items",
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
    });


    // ****************************************
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();
        let name = $("#product_name").val();
        let UserID = $("#user_id").val();
        let available = $("#pet_available").val() == "true";
        let gender = $("#pet_gender").val();
        let recordTime = $("#record_time").val();

        let data = {
            "name": name,
            "UserID": UserID,
            "available": available,
            "gender": gender,
            "recordTime": recordTime
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/shopcarts/${shopcart_id}`,
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
    // Retrieve a Pet
    // ****************************************

    $("#retrieve-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}`,
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
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Pet has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#shopcart_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#product_name").val();
        let UserID = $("#user_id").val();
        let available = $("#pet_available").val() == "true";

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
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
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
            table += '<th class="col-md-2">Available</th>'
            table += '<th class="col-md-2">Gender</th>'
            table += '<th class="col-md-2">recordTime</th>'
            table += '</tr></thead><tbody>'
            let firstPet = "";
            for(let i = 0; i < res.length; i++) {
                let pet = res[i];
                table +=  `<tr id="row_${i}"><td>${pet.id}</td><td>${pet.name}</td><td>${pet.UserID}</td><td>${pet.available}</td><td>${pet.gender}</td><td>${pet.recordTime}</td></tr>`;
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
