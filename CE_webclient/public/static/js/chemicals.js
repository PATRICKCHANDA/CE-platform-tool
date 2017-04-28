// http://stackoverflow.com/questions/1841916/how-to-avoid-global-variables-in-javascript

// use closure to avoid global variable
var CHEMICALS = (function () {
    var all_chemicals = {};
    
    function save_all_chemicals(data) {
        for (var i = 0; i < data.length; ++i) {
            chem_id = data[i][0];
            chem_detail = data[i][1];
            all_chemicals[chem_id] = chem_detail;
        }
    }

    return {
        load_all_chemicals: function(func) {
            $.getJSON(url_get_chemicals)
            .done(function (data) {
                if (data.length > 0) {
                    save_all_chemicals(data);
                    // execute some callback
                    if (func)
                        func();
                }
            })
            .fail(function (status, err) {
                console.log("Error: Failed to load chemicals from DB.");
            })
        },

        get_a_chemical: function(chem_id) {
            return all_chemicals[chem_id];
        },

        get_all_chemicals: function () {
            return all_chemicals;
        },

        get_name: function (chem_id) {
            return all_chemicals[chem_id].name;
        }
    };

})();
