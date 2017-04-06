var g_factory_id;

//! button onClick event handler to submit the changes and update the results in the webpage
$("#btn_confirm_change_input").on("click", function() {
    // get the current rf_id from the drop-down box
    var rf_id = $("#factory_processes_info > select").val();
    // get the total profit of the factory
    total_profit = $("#factory_total_profit > h5").text();
    // get rid of the unit
    var pos = total_profit.indexOf(" ");
    total_profit = total_profit.substr(0, pos);
    // get the profit of current product_line
    product_line_profit = $("#factory_product_profit > h5").text();
    pos = product_line_profit.indexOf(" ");
    product_line_profit = product_line_profit.substr(0, pos);
    var profit_of_other_processes = Number(total_profit) - Number(product_line_profit);
    apply_model_basis_info_changes(g_factory_id, rf_id, profit_of_other_processes);
});

/*  \brief react on the name click event!
 \param factory_id
 \param component_id_or_name: for emission, it is a string value, for others, it is an ID
 \param as_supplier: if true, this factory is the supplier, we want to find the factory consume this component
                     if false, this factory is the comsumer, we want to find the factory supply this component
 \param data_url: contains factory_id/component_type/component_name/as_supplier
 */
function name_click_handler(data_url) {
    resetFactoryColor();
    // waiting for the results
    $.getJSON(url_get_factory_ids_dealing_with_component + data_url)
    .done(function (data) {
        if (data) {
            // show them in a table
            // mark those factories in the map
            for (var i = 0; i < data.length; ++i)
                markFactoryColor(data[i]);
        }           
    })
    .fail(function (status, err) {
        console.log("Error: failed to load factory supplying or comsuming the component", factory_id);
    })

}

/*! \brief create a new row in the table and add contents into the row
 \param contents: array of data
 \param value_editable: array of boolean
 \param contents_id: array of string used as id for <td>
 \param compoent_type: value as emission, chemical, utility
 \param is_supplier: boolean
 */
function add_a_table_row(a_table_body, contents, value_editable, contents_id, component_type, is_supplier) {
    var aRow = a_table_body.appendChild(document.createElement('tr'));
    for (var i = 0; i < contents.length; ++i) {
        editable = value_editable[i];
        if (!editable) {
            var aCell = aRow.appendChild($('<td>' + contents[i] + '</td>').get(0));
            // if it has contents_id, then this cell is clickable
            if (contents_id[i] != null && contents_id[i] != '') {
                if (component_type) {
                    aCell.innerText = '';
                    alink = aCell.appendChild($("<a href='#'>" + contents[i] + "</a>").get(0));
                    // save the factory_id, component_type, component_id/name, is_supplier in the link attribute
                    alink.data = g_factory_id + "/" + component_type + "/" + contents_id[i] + "/" + (+is_supplier);
                    alink.onclick = function (e) {
                        //console.log(e.target.data);
                        name_click_handler(e.target.data);
                    }
                }
            }
        }
        else
            aRow.appendChild($('<td class="bg-info" contenteditable="true" id=' + contents_id[i] + '>' + contents[i] + '</td>').get(0));
    }
}

/*! \brief get the table "process_input" changed value,
           submit the changes, get the results from server and update the results in the current page
 \param profit_of_other_processes: total profit of all processes exclude current process
 */
function apply_model_basis_info_changes(factory_id, rf_id, profit_of_other_processes) {
    // read the table, loop through each tr
    var request_content = {};
    var all_rows = $("#process_input > table tbody tr");
    if (all_rows.length > 0) {
        // the first row: cell 1 with id as chem_id, value is the quantity, otherwise we will get sth. like 2:100000, hard to use on server side
        request_content.id = parseInt(all_rows[0].cells[1].id);
        request_content.quantity = Number(all_rows[0].cells[1].innerHTML);
        price_name = all_rows[0].cells[3].id;
        price_value = Number(all_rows[0].cells[3].innerHTML);
        request_content[price_name] = price_value;
        //request_content.
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
        .done(function(data) {
            console.log( "response got: " + data.msg );
        })
        .fail(function (err) {
            console.log(err)
        });

        // waiting for the results
        $.getJSON(url_get_factory_productline + factory_id + "/" + rf_id)
        .done(function (data) {
            if (data)
                // update the total factory profit
                factory_total_profit = profit_of_other_processes + data.process_annual_revenue
                value_unit = data.revenue_unit
                $("#factory_total_profit > h5").text(factory_total_profit + " " + value_unit);
                // todo: for performance -> update the tables instead of clear then rebuild the table
                display_a_product_process_details(factory_id, data);

        })
        .fail (function (status, err) {
            console.log("Error: failed to load product from factory", factory_id);
        })
    }
}

/*! \brief display ONE product line contents: material use, emission, byproducts, utilities
 \param factory_id:
 \param product_line_info: 1 product line information including product(s), byproduct(s), material, emission
 */
function display_a_product_process_details(factory_id, product_line_info) {
    // each product_line may have more than 1 product!
    // the total revenue of a specified product line, a factory may contain more than 1 product line
    // and a product_line may contain more than 1 product!
    var total_value = 0;
    var value_unit = "";
    for (var i=0; i< product_line_info.products.length;++i) {
        var product_info = product_line_info.products[i];
        total_value += product_info.annual_value;
        value_unit = product_info.currency;
    }

    $("#factory_product_income > h5").text(total_value + " "+ value_unit);
    $("#factory_product_profit > h5").text(product_line_info.process_annual_revenue + " "+ product_line_info.revenue_unit);

    fill_model_basis_table(product_line_info.process_basis, product_line_info.products, factory_id);
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
    // set the global variable
    g_factory_id = factory_id;
    factory_total_profit = data['total_profit'];

    // show total profit of the factory
    $("#factory_total_profit > h5").text(factory_total_profit + " " + data['profit_unit']);
    // clear any previous options
    $("#factory_processes_info > select").empty();

    // display all the product line's product in a drop-down box
    var product_processes = "";
    var product_lines = data['product_lines'];
    for (var i=0; i < product_lines.length; ++i) {
        rf_id = product_lines[i][0];  // reaction_formula id
        process_name = product_lines[i][1].rf_name
        product_processes += '<option value="' + rf_id + '">' + process_name + '</option>'
    }
    $("#factory_processes_info > select").append(product_processes);

    // bind a event handler for the drop-down box
    $("#factory_processes_info > select").on('change', function() {
        product_process_change_handler(factory_id, this.value, product_lines);
    });

    if (product_lines.length > 0)
        // display ONLY one factory's product line, even this factory has more than 1 product line
        display_a_product_process_details(factory_id, product_lines[0][1]);
    else {// clear all data
        $("#info-col table tr").remove();
        $("#factory_product_income > h5").text("");
        $("#factory_product_profit > h5").text("");
    }
}

/*! \brief a general add contents to table function
 \param component_type: chemical, utility, emission or factory
 */
function fill_table_content(a_table, info, component_type, is_supplier) {
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
                [an_item.id, '', 'value_per_unit_' + an_item.id, ''],
                component_type, is_supplier
            );
        }
    }
}

function fill_byproducts_table(byproducts_info) {
    // insert into table
    $table = $("#byproducts > table");
    fill_table_content($table, byproducts_info, "chemical", true);
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
            add_a_table_row(tblbody, [emission_info[i].name, emission_info[i].quantity], [false, false], [emission_info[i].name, ''], "emission", true);
        }
    }
}

function fill_material_table(material_info) {
    // insert into table
    $table = $("#material > table");
    fill_table_content($table, material_info, "chemical", false);
}

/*
 \param process_basis_info: information of the process, such days/hours of production, temperature, pressure, etc
 \param products_info: array of products
 \param factory_id: unique object_id of the factory in the database
 \param profit_of_other_processes: total profit except the current product_line
*/
function fill_model_basis_table(process_basis_info, products_info, factory_id) {
    $table = $("#process_input > table");
    // clear the current table content
    $table.find("tr").remove();
    var days_production = process_basis_info.DOP;
    var hours_production = process_basis_info.HOP;
    var conversion = process_basis_info.conversion;
    var inlet_pressure = process_basis_info.inlet_P;
    var inlet_temperature = process_basis_info.inlet_T;
    $table.append('<thead><tr class="table-info"><th>名称</th><th>数值每年</th><th>单位</th><th>单位价格</th><th>价格单位</th></tr></thead>');
    var tblbody = $table.get(0).appendChild(document.createElement('tbody'));
    for (var i=0; i <products_info.length; ++i) {
        // for multiple products of 1 product line, user can only edit the quantity of 1 product
        // because other products will be change during the calculation and displayed again
        add_a_table_row(tblbody,
            [products_info[i].name, products_info[i].quantity, products_info[i].unit, products_info[i].value_per_unit, products_info[i].currency_value_per_unit],
            [false, i==0?true:false, false, true, false],
            [products_info[i].id, products_info[i].id, '', 'value_per_unit_' + products_info[i].id, ''],
            'chemical', true
        );
    }
//    add_a_table_row(tblbody,
//        ["单位成本", product_info.value_per_unit, product_info.currency_value_per_unit],
//        [false, true, false],
//        ['', 'value_per_unit', '']
//    );
    add_a_table_row(tblbody, ["年生产天数", days_production, "天"], [false, true, false], ['', 'DOP', ''], null, null);
    add_a_table_row(tblbody, ["生产小时数/天", hours_production, "小时"], [false, true, false], ['', 'HOP', ''], null, null);
    add_a_table_row(tblbody, ["转换效率(0~1)", conversion, "-"], [false, true, false], ['', 'conversion', ''], null, null);
//    add_a_table_row(tblbody, ["入口压力", inlet_pressure, "bar"], [false, true, false]);
//    add_a_table_row(tblbody, ["入口温度", inlet_temperature, "C"], [false, true, false]);
    // todo: add basic reaction_formula information

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
                [utility_info[i].id, '', '', 'value_per_unit', ''],
                "utility", false // use those utilities
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
