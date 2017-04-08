var OVERVIEW = (function () {
    return {
        show_area_total_revenue: function () {
            $.getJSON(url_whole_area_revenue)
            .done(function (data) {
                if (data) {
                    var total_value = data[0];
                    var value_unit = data[1];
                    $("#area_total_revenue").text("已知区域内总净收入: " + total_value + " " + value_unit);
                }
            })
            .fail(function (status, err) {

            })
        }
    }
})();
