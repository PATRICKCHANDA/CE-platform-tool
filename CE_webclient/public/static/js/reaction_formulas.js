function add_label_and_textfield(div, label_name) {
    var $new_row = div.append('<div class="row"><div>');
    var label = '<label class="col-sm-6">' + label_name + ':</label>';
    var textfield = '<input type="text" class="col-sm-4">';
    $new_row.append(label);
    $new_row.append(textfield);
}

/*  \brief insert all the process id and names into a drop-down box
 */
function display_all_reactions(data) {
    var $select = $("#all_processes_info .panel-heading > select");
//    $select.empty();
    var processes = "";
    for (var i = 0; i < data.length; ++i) {
        rf_id = data[i][0];
        rf_detail = data[i][1];
        $option = $("<option value="+rf_id+"></option>").text(rf_detail.name);
        var product_ids = [];
        for (var p = 0; p < rf_detail.products.length; ++p)
            product_ids.push(rf_detail.products[p].chem_id);
        $option.attr("product_ids", product_ids);
        //processes += '<option value="' + rf_id + '">' + rf_detail.name + '</option>';
        $select.append($option);
        // todo: draw a chart to show the material input and the products!
    }
    //$("#all_processes_info > select").append(processes);

    $select.on('change', function (e) {
        $("#info_add_process").text("");
        var $div = $("#process_product_name_quantity");
        $div.children().remove();
        var product_ids = $("option:selected", this).attr("product_ids").split(',');
        for (var i = 0; i < product_ids.length; ++i) {
            // add the chemical_name and a textarea
            chem_name = CHEMICALS.get_name(product_ids[i]);
            add_label_and_textfield($div, chem_name);
        }
    })
}

/* \brief btn_add_process_to_factory onclick event: which send the request to server: adding the process into the factory, and
          get response back
 */
$("#btn_add_process_to_factory").on('click', function (e) {
    // get the process id
    var rf_id = $("#all_processes_info .panel-heading > select").val();
    if (rf_id == null) {
        $("#info_add_process").text('请选择一项工艺');
        return;
    } 
    if (g_factory_id == null) {
        $("#info_add_process").text('请点击地图选择企业');
        return;
    }

    // add this reaction_formula into factory
    url = url_insert_rf_to_factory + rf_id + "/" + g_factory_id;
    $.getJSON(url)
    .done(function (data) {
        if (data) {
            if (data.hasOwnProperty('info'))
                $("#info_add_process").text(data.info);
            else if (data.hasOwnProperty('error'))
                $("#info_add_process").text(data.error);
            else
                $("#info_add_process").text("");
                display_factory_processes_info(g_factory_id, data);
            // display
            // show value of the factory
            // show added value of the whole area
            OVERVIEW.show_area_total_revenue();
        }
    })
    .fail(function (status, err) {
        console.log("Error: failed to add process to factory ", factory_id);
    })
});