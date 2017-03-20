
function collapse() {
        $("#map-col").toggleClass("col-md-12");
        $("#map-col").toggleClass("col-md-4");

        // collapse the info and analysis block
        $("#info-col").toggleClass("collapse");
        $("#info-col").toggleClass("col-md-4");

        $("#analysis-col").toggleClass("collapse");
        $("#analysis-col").toggleClass("col-md-4");
}

// when click on the collapse button, collapse the the page
function changeLayout(btn_clicked) {
    if (btn_clicked || ! $('#map-col').hasClass("col-md-4")) {
        collapse();
    }
}

