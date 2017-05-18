var CHEMICAL_PROCESS = (function () {
    /* data saved in this way:
        { id:{rf_name: "bbbb", products_ids: [], reactants_ids:[]}
        , ...
        }
    */
    var all_chemical_process = {};

    function save_all_process(data) {
        for (var i = 0; i < data.length; ++i) {
            rf_id = data[i][0];
            rf_detail = data[i][1];
            a_rf = {rf_name: rf_detail.name};
            a_rf["product_ids"] = [];
            a_rf["reactants_ids"] = [];
            for (var p = 0; p < rf_detail.products.length; ++p)
                a_rf["product_ids"].push(rf_detail.products[p].chem_id);
            for (var p in rf_detail.reactants)
                a_rf["reactants_ids"].push(rf_detail.reactants[p].chem_id);
            all_chemical_process[rf_id] = a_rf;
        }
    }

    return {
        load_all_reactions: function (func) {
            $.getJSON(url_get_reactions)
            .done(function (data) {
                if (data.length > 0) {
                    save_all_process(data);
                    if (func)
                        func();
                }                    
            })
            .fail(function (status, err) {
                console.log("Error: Failed to load reactions from DB.");
            })
        },

        get_all_chemical_processes: function() {
            return all_chemical_process;
        },

        get_a_chemical_process: function (rf_id) {
            return all_chemical_process[rf_id];
        },
        //post_process_to_server: function (request) {
        //    $.ajax({
        //        type: "POST",
        //        url: url_post_reaction_formula,
        //        data: JSON.stringify(request),
        //        dataType: 'json',
        //        contentType: 'application/json; charset=utf-8'
        //    })
        //    .done(function (data) {
        //        return data.msg;
        //    })
        //    .fail(function (err) {
        //        return "Oops!Failed to upload process into server."

        //    });
        //}
    }
})();

