//! display product process contents: material use, emission, byproducts, utilities
function display_a_product_process_details(process_info) {
    fill_model_basis_table(process_info.process_basis);
    // process_info.material: array
    fill_material_table(process_info.material);
    // process_info.emissions: object
    fill_emission_table(process_info.emissions);
    // process_info.utilities: array
    fill_utilities_table(process_info.utilities);
    // process_info.by-products: array
    fill_byproducts_table(process_info.by-products);
}

/*! \brief called by layer feature onclick event handler,
           add the products into the drop-down list, and display the details of the first product
*/
function display_factory_processes_info(factory_id, data) {
    // clear any previous options
    $("#factory_processes_info > select").empty();
    // bind a event handler
    $("#factory_processes_info > select").on('change', function() {
        product_process_change_handler(factory_id, this.value);
    });
    // display all the product line in a drop-down box
    var product_processes = "";
    for (var i=0; i < data.length; ++i) {
        process_id = data[i][0];
        process_name = data[i][1].rf_name
        product_processes += '<option value="' + process_id + '">' + process_name + '</option>'
    }
    $("#factory_processes_info > select").append(product_processes);

    if (data.length > 0)
        // display ONLY one factory's product line's even this factory has more than 1 product line
        display_a_product_process_details(data[0][1]);
    else // clear all data
        $("#info-col table tr").remove();
}


//! handler of product process drop-down list value change handler
function product_process_change_handler(factory_id, rf_id) {
    console.log(rf_id + " is selected.");
    // todo: query data for this process of this factory
    // todo: display
//    display_a_product_process_details(process_info);
}

function add_a_table_row(a_table_body, contents, value_editable) {
    var aRow = a_table_body.appendChild(document.createElement('tr'));
    for (var i = 0; i < contents.length; ++i) {
        editable = value_editable[i];
        if (!editable)
            aRow.appendChild($('<td>' + contents[i] + '</td>').get(0));
        else
            aRow.appendChild($('<td contenteditable="true">' + contents[i] + '</td>').get(0));
    }
}

function fill_emission_table(emission_info) {
}

function fill_material_table(material_info) {
}

function fill_model_basis_table(process_info) {
    var product_info = process_info.products[0];
    var days_production = process_info.DOP;
    var hours_production = process_info.HOP;
    var conversion = process_info.conversion;
    var inlet_pressure = process_info.inlet_P;
    var inlet_temperature = process_info.inlet_T;
    // insert into table
    $table = $("#process_input > table");
    // clear the current table content
    $table.find("tr").remove();
    $table.addClass('table table-striped');
    $table.append('<thead><tr><th>名称</th><th>数值</th><th>单位</th></tr></thead>');
    var tblbody = $table.get(0).appendChild(document.createElement('tbody'));
    add_a_table_row(tblbody, [product_info.name, product_info.quantity, product_info.unit],  [false, true, false]);
    add_a_table_row(tblbody, ["年生产天数", days_production, "天"], [false, true, false]);
    add_a_table_row(tblbody, ["生产小时数/天", hours_production, "小时"],  [false, true, false]);
    add_a_table_row(tblbody, ["转换效率(0~1)", conversion, "-"],  [false, true, false]);
    add_a_table_row(tblbody, ["入口压力", inlet_pressure, "bar"],  [false, true, false]);
    add_a_table_row(tblbody, ["入口温度", inlet_temperature, "C"],  [false, true, false]);
    // todo: add basic reaction_formula information
}

function fill_utilities_table(utility_info) {
}