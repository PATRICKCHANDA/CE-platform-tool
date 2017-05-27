var info_analysis_col_collapsed = true;

function collapse() {
        $("#map-col").toggleClass("col-md-12");
        $("#map-col").toggleClass("col-md-4");

        // collapse the info and analysis block
        $("#info-col").toggleClass("collapse");
        $("#info-col").toggleClass("col-md-4");

        $("#analysis-col").toggleClass("collapse");
        $("#analysis-col").toggleClass("col-md-4");
}

//! change the page layout
function changeLayout(btn_clicked) {
    if (!$("div#scenario_compare-col").hasClass("col-md-12")) {
        // when click on the collapse button, toggle the the page
        // when click on the layer feature, always open the info block or keep the info block open
        if (btn_clicked || ! $('#map-col').hasClass("col-md-4")) {
            $("#btn_full_view > i").toggleClass("fa-plus-circle");
            $("#btn_full_view > i").toggleClass("fa-minus-circle");
            collapse();
        }
    }
    if ($("#btn_full_view > i").hasClass("fa-plus-circle"))
        info_analysis_col_collapsed = true;
    else
        info_analysis_col_collapsed = false;

}

//! show the scenario compare part, hidden all other parts
function show_scenario_compare() {
    if (!$("div#scenario_compare-col").hasClass("col-md-12")) {
        // open part
        // collapse map column
        $("div#map-col").toggleClass("collapse");
        

        $("div#scenario_compare-col").toggleClass("collapse");
        $("div#scenario_compare-col").toggleClass("col-md-12");
    }
    else {
        // close the scenario_compare-col part

        // un-collapse map-col
        $("div#map-col").toggleClass("collapse");
        // collapse scenari_compare-col
        $("div#scenario_compare-col").toggleClass("collapse");
        $("div#scenario_compare-col").toggleClass("col-md-12");

    }

    // restore the info-col and analysis-col
    if (!info_analysis_col_collapsed) {
        // collapse the info and analysis block
        $("#info-col").toggleClass("collapse");
        $("#info-col").toggleClass("col-md-4");

        $("#analysis-col").toggleClass("collapse");
        $("#analysis-col").toggleClass("col-md-4");
    }
}

