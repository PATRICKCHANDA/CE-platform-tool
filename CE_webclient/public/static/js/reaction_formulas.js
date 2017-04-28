﻿var CHEMICAL_PROCESS = (function () {
    var all_chemical_process = {};

    return {
        load_all_reactions: function () {

        },
        get_a_chemical_process: function (rf_id) {
            return all_chemical_process[rf_id];
        },
    }
})();

/* \brief display the name of the product and an input field
*/
function add_label_and_textfield(div, label_name, chemical_id) {
    var $new_row = $('<div class="row"></div>');
    var label = '<label class="col-sm-6" chemical_id="'+ chemical_id + '">' + label_name + ':</label>';
    var textfield = '<input type="text" class="col-sm-4" value=100000>';
    $new_row.append(label);
    $new_row.append(textfield);
    div.append($new_row);
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
        // remove all the products info of previous process
        $div.children().remove();
        var product_ids = $("option:selected", this).attr("product_ids").split(',');
        for (var i = 0; i < product_ids.length; ++i) {
            // add the chemical_name and a textarea
            chem_name = CHEMICALS.get_name(product_ids[i]);
            add_label_and_textfield($div, chem_name, product_ids[i]);
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

    // todo:　ｓｅｎｄ
    var request_content = {};
    // loop through each row with label and input
    $("#process_product_name_quantity").children('div').each(function () {
        var chemical_id = $(this).children('label').attr('chemical_id');
        var volume = $(this).children('input').val();
        request_content[chemical_id] = volume;
    });

    // todo: post the data to the server
    //$.ajax({
    //    type: "POST",
    //    url: url_insert_rf_to_factory + rf_id + "/" + g_factory_id,
    //    data: JSON.stringify(request_content),
    //    dataType: 'json',
    //    contentType: 'application/json; charset=utf-8'
    //})
    //.done(function (data) {
    //    console.log("response got: " + data.msg);
    //})
    //.fail(function (err) {
    //    console.log(err)
    //});

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
            //OVERVIEW.show_area_total_revenue();
        }
    })
    .fail(function (status, err) {
        console.log("Error: failed to add process to factory ", factory_id);
    })
});