
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
    // when click on the collapse button, toggle the the page
    // when click on the layer feature, always open the info block or keep the info block open
    if (btn_clicked || ! $('#map-col').hasClass("col-md-4")) {
        $("#btn_full_view > i").toggleClass("fa-plus-circle");
        $("#btn_full_view > i").toggleClass("fa-minus-circle");
        collapse();
    }
}

