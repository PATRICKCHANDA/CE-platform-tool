/*! \brief create a new row in the table and add contents into the row
 \param contents: array of data
 \param value_editable: array of boolean
 \param contents_id: array of string used as id for <td>
 */
function add_a_table_row(a_table_body, contents, value_editable, contents_id) {
    var aRow = a_table_body.appendChild(document.createElement('tr'));
    for (var i = 0; i < contents.length; ++i) {
        editable = value_editable[i];
        if (!editable)
            aRow.appendChild($('<td>' + contents[i] + '</td>').get(0));
        else
            aRow.appendChild($('<td class="bg-info" contenteditable="true" id='+ contents_id[i] + '>' + contents[i] + '</td>').get(0));
    }
}

/*! \brief get the table "process_input" changed value,
           submit the changes, get the results from server and update the results in the current page
 */
function apply_model_basis_info_changes(factory_id, rf_id) {
    // read the table, loop through each tr
    var request_content = {};
    var all_rows = $("#process_input > table tbody tr");
    if (all_rows.length > 0) {
        // the first row: cell 1 with id as chem_id, value is the quantity
        request_content.id = parseInt(all_rows[0].cells[1].id);
        request_content.quantity = Number(all_rows[0].cells[1].innerHTML);
        // other rows
        for (var r = 1; r < all_rows.length; ++r) {
            var row = all_rows[r];
            for (var i=0; i < row.cells.length; ++i ) {
                var cell = row.cells[i];
                if (cell.contentEditable=="true") {
                    var name = cell.id;
                    var value = Number(cell.innerHTML);
                    request_content[name] = value;
                }
            }
        }

        // post the data to the server
        $.ajax({
            type: "POST",
            url: url_calc_factory_productline + factory_id + "/" + rf_id,
            data: JSON.stringify(request_content),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8'
        })
        .done(function(msg) {
            console.log( "request send: " + msg );
        })
        .fail(function (err) {
            console.log(err)
        });

//        // waiting for the results
//        $.getJSON(url_calc_factory_productline + factory_id + "/" + rf_id)
//        .done(function (data) {
//            if (data.length > 0)
//                console.log(data[0].rf_name)
//            display_factory_processes_info(factory_id, data);
//        })
//        .fail (function (status, err) {
//            console.log("Error: failed to load products from factory", feature.id);
//        })
        // update the tables
    }
}

/*! \brief display ONE product line contents: material use, emission, byproducts, utilities
 */
function display_a_product_process_details(factory_id, product_line_info) {
    // each product_line has one product!
    var product_info = product_line_info.products[0];
    $("#factory_product_income > h5").text(product_info.annual_value + " "+ product_info.currency);
    $("#factory_product_profit > h5").text(product_line_info.process_annual_revenue + " "+ product_info.currency);
    fill_model_basis_table(product_line_info.process_basis, product_info, factory_id);
    // process_info.material: array
    fill_material_table(product_line_info.material);
    // process_info.emissions: object
    fill_emission_table(product_line_info.emissions);
    // process_info.utilities: array
    fill_utilities_table(product_line_info.utilities);
    // process_info.by-products: array
    fill_byproducts_table(product_line_info.by_products);
}

/*! \brief called by layer Feature onclick event handler,
           add the products into the drop-down list, and display the details of the first product
*/
function display_factory_processes_info(factory_id, data) {
    // clear any previous options
    $("#factory_processes_info > select").empty();

    // display all the product line's product in a drop-down box
    var product_processes = "";
    for (var i=0; i < data.length; ++i) {
        rf_id = data[i][0];  // reaction_formula id
        process_name = data[i][1].rf_name
        product_processes += '<option value="' + rf_id + '">' + process_name + '</option>'
    }
    $("#factory_processes_info > select").append(product_processes);

    // bind a event handler for the drop-down box
    $("#factory_processes_info > select").on('change', function() {
        product_process_change_handler(factory_id, this.value, data);
    });

    if (data.length > 0)
        // display ONLY one factory's product line, even this factory has more than 1 product line
        display_a_product_process_details(factory_id, data[0][1]);
    else {// clear all data
        $("#info-col table tr").remove();
        $("#factory_product_income > h5").text("");
        $("#factory_product_profit > h5").text("");
    }
}

/*! \brief a general add contents to table function
 */
function fill_table_content(a_table, info) {
    // clear the current table content
    a_table.find("tr").remove();
    if (info.length > 0) {
        quantity_unit = info[0].unit;
        currency = info[0].currency;
        currency_value_per_unit = info[0].currency_value_per_unit;
        a_table.append('<thead><tr class="table-info"><th>名称</th><th>数值每年(单位:'+ quantity_unit +')</th><th>单位成本(' + currency_value_per_unit + ')</th><th>年成本(单位:'+ currency +')</th></tr></thead>');
//        $table.children('tr:first').addClass('table-info');
        var tblbody = a_table.get(0).appendChild(document.createElement('tbody'));
        for (var i = 0; i < info.length; ++i) {
            var an_item = info[i];
            add_a_table_row(tblbody,
                [an_item.name, an_item.quantity, an_item.value_per_unit, an_item.annual_value],
                [false, false, true, false],
                ['', '', 'value_per_unit', '']
            );
        }
    }
}

function fill_byproducts_table(byproducts_info) {
    // insert into table
    $table = $("#byproducts > table");
    fill_table_content($table, byproducts_info);
}

function fill_emission_table(emission_info) {
    // insert into table
    $table = $("#emission > table");
    // clear the current table content
    $table.find("tr").remove();
    if (emission_info.length > 0) {
        quantity_unit = emission_info[0].unit;
        $table.append('<thead><tr><th>名称</th><th>年排放量(单位: '+ quantity_unit +')</th></tr></thead>');
        var tblbody = $table.get(0).appendChild(document.createElement('tbody'));
        for (var i=0; i < emission_info.length; ++i) {
            add_a_table_row(tblbody, [emission_info[i].name, emission_info[i].quantity], [false, false]);
        }
    }
}

function fill_material_table(material_info) {
    // insert into table
    $table = $("#material > table");
    fill_table_content($table, material_info);
}

function fill_model_basis_table(process_basis_info, product_info, factory_id) {
    $table = $("#process_input > table");
    // clear the current table content
    $table.find("tr").remove();
    var days_production = process_basis_info.DOP;
    var hours_production = process_basis_info.HOP;
    var conversion = process_basis_info.conversion;
    var inlet_pressure = process_basis_info.inlet_P;
    var inlet_temperature = process_basis_info.inlet_T;
    $table.append('<thead><tr class="table-info"><th>名称</th><th>数值每年</th><th>单位</th></tr></thead>');
    var tblbody = $table.get(0).appendChild(document.createElement('tbody'));
    add_a_table_row(tblbody,
        [product_info.name, product_info.quantity, product_info.unit],
        [false, true, false],
        ['', product_info.id, '']
    );
    add_a_table_row(tblbody,
        ["单位成本", product_info.value_per_unit, product_info.currency_value_per_unit],
        [false, true, false],
        ['', 'value_per_unit', '']
    );
    add_a_table_row(tblbody, ["年生产天数", days_production, "天"], [false, true, false], ['', 'DOP', '']);
    add_a_table_row(tblbody, ["生产小时数/天", hours_production, "小时"], [false, true, false], ['', 'HOP', '']);
    add_a_table_row(tblbody, ["转换效率(0~1)", conversion, "-"], [false, true, false], ['', 'conversion', '']);
//    add_a_table_row(tblbody, ["入口压力", inlet_pressure, "bar"], [false, true, false]);
//    add_a_table_row(tblbody, ["入口温度", inlet_temperature, "C"], [false, true, false]);
    // todo: add basic reaction_formula information

    //! button onclick event handler to submit the changes and update the results in the webpage
    $("#btn_confirm_change_input").on("click", function() {
        // get the current rf_id from the drop-down box
        var rf_id = $("#factory_processes_info > select").val();
        apply_model_basis_info_changes(factory_id, rf_id)
    })
}

function fill_utilities_table(utility_info) {
    $table = $("#utilities > table");
    // clear the current table content
    $table.find("tr").remove();
    if (utility_info.length > 0 ) {
        // insert into table
        currency = utility_info[0].currency;
        currency_value_per_unit = utility_info[0].currency_value_per_unit;
        $table.append('<thead><tr><th>名称</th><th>数值(每秒)</th><th>单位</th><th>单位成本('+currency_value_per_unit+')</th><th>年成本(单位:' + currency + ')</th></tr></thead>');
        var tblbody = $table.get(0).appendChild(document.createElement('tbody'));
        for (var i=0; i < utility_info.length; ++i) {
            add_a_table_row(tblbody,
                [utility_info[i].name, utility_info[i].quantity, utility_info[i].unit, utility_info[i].value_per_unit, utility_info[i].annual_value],
                [false, false, false, true, false],
                ['', '', '', 'value_per_unit', '']
            );
        }
    }
}

//! handler of product process drop-down list value change handler
function product_process_change_handler(factory_id, rf_id, data) {
    console.log(rf_id + " is selected.");
    // query data for this process of this factory
    var product_line_info = $.grep(data, function(e) {
        return e[0] == rf_id;
    });
    // display
    if (product_line_info.length == 1)
        display_a_product_process_details(factory_id, product_line_info[0][1]);
}
