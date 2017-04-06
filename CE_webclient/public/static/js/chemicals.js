// http://stackoverflow.com/questions/1841916/how-to-avoid-global-variables-in-javascript

// use closure to avoid global variable
var CHEMICALS = (function () {
    var all_chemicals = {};
    
    function test() { };

    return {
        display_all_chemicals: function (data) {
            for (var i = 0; i < data.length; ++i) {
                chem_id = data[i][0];
                chem_detail = data[i][1];
                all_chemicals[chem_id] = chem_detail;
            }
        },

        get_all_chemicals: function () {
            return all_chemicals;
        },

        get_name: function (chem_id) {
            return all_chemicals[chem_id].name;
        }
    };

})();
