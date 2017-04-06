/*  \brief insert all the process id and names into a drop-down box
 */
function display_all_reactions(data) {
    $("#all_processes_info > select").empty();
    var processes = "";
    for (var i = 0; i < data.length; ++i) {
        rf_id = data[i][0];
        rf_detail = data[i][1];
        processes += '<option value="' + rf_id + '">' + rf_detail.name + '</option>';
        // todo: draw a chart to show the material input and the products!
    }
    $("#all_processes_info > select").append(processes);
    $("#all_processes_info > select").on('change', function (e) {       
        var $label = $("<label>").text(data[this.value][1].name + ": ").addClass("col-sm-6");
        var $textarea = $("<textarea>").addClass("col-sm-6");
        $("#process_product_name_quantity").append($label);
        $("#process_product_name_quantity").append($textarea);
    })
}

/* \brief onclick event: which send the request to server: adding the process into the factory, and
          get response back
 */
$("#btn_add_process_to_factory").on('click', function (e) {
    // get the process id
    var rf_id = $("#all_processes_info > select").val();
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
                display_factory_processes_info(g_factory_id, data);
            // display
            // show value of the factory
            // show added value of the whole area
        }
    })
    .fail(function (status, err) {
        console.log("Error: failed to add process to factory ", factory_id);
    })
});