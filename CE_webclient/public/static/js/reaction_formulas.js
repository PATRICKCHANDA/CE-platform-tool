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
}

$("#btn_add_process_to_factory").on('click', function (e) {
    // get the process id
    var rf_id = $("#all_processes_info > select").val();
    // add this reaction_formula into factory
    url = url_insert_rf_to_factory + "/" + rf_id + "/" + g_factory_id;
    $.getJSON(url)
    .done(function (data) {
        if (data) {
            // display
            // show value of the factory
            // show added value of the whole area
        }
    })
    .fail(function (status, err) {
        console.log("Error: failed to add process to factory ", factory_id);
    })
});