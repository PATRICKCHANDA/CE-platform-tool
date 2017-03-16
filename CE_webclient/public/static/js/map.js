$(document).ready(function () {
    var custom_bounds = new L.LatLngBounds(
	    new L.LatLng(21.9, 113.12),
	    new L.LatLng(22.000000, 113.3));

    var mymap = L.map('map-col', { zoomControl: false}).fitBounds(custom_bounds);
//    mymap.crs = L.CRS.EPSG4326;
    // http://stackoverflow.com/questions/22926512/customize-zoom-in-out-button-in-leaflet-js
    // http://leafletjs.com/reference.html#control
    L.control.zoom({
        zoomInTitle: '放大',
        zoomOutTitle: '缩小'
    }).addTo(mymap);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(mymap);

    // add weather images as tilelayer
    var options = {
        minZoom: 0,
        maxZoom: 10,
        opacity: 0.5,
        attribution: '',
        format: 'png',
        tms: true    // for MapTiler generated, set to false;
    };

//    var data = {
//	'type' : 'FeatureCollection',
//	'features' : [{"type": "Feature",
//	                "id": 7,
//	                "geometry": {
//	                    "coordinates": [[[113.18285500925758, 21.97158131878827], [113.17912522042961, 21.971939952329425], [113.17919694713783, 21.964336921256997], [113.18271155584114, 21.96440864796523], [113.18285500925758, 21.97158131878827]]],
//	                    "type": "Polygon"
//	                },
//	                "properties": {"name": "powerplant"}
//	               },
//	               {"type": "Feature", "id": 8
//	               , "geometry": {"coordinates": [[[113.20939389130285, 21.983918312603915], [113.20473165526788, 21.987863281556592], [113.2022212204798, 21.985137666643833], [113.20494683539256, 21.982555505147538], [113.2073855434724, 21.98169478464877], [113.20939389130285, 21.983918312603915]]], "type": "Polygon"}, "properties": {"name": "BP factory"}
//	               },
//	               {"type": "Feature", "id": 9, "geometry": {"coordinates": [[[113.22287851245018, 21.96648872250391], [113.23040981681439, 21.959387778389097], [113.23672176713866, 21.95881396472325], [113.23887356838557, 21.965341095172224], [113.23550241309874, 21.97029023804013], [113.22589103419585, 21.96921433741667], [113.22287851245018, 21.96648872250391]]], "type": "Polygon"}, "properties": {"name": "wastetreatment"}}
//	              ]
//    };
//    L.geoJSON(data).addTo(mymap);
    loadGeometries(mymap);
//    $.getJSON(url_get_factory)
//    .done(function (data) {
//        L.geoJson(data).addTo(mymap);
//    })
//    .fail(function (status, err) {
//        console.log("Error: Failed to load factories from DB.");
//    })
    /*  DOM layout of the modalDiaglog showing the object Properties
    DOM
        - div
        - div
        - table
            - thead
                - tr
                    -th th
            - tbody
                - tr
                    -td td td
                - tr
                    -td td td
        - div
          - button button  button
        - div
    */
    $("#btn_full_view").on('click', function() {
        changeLayout();
        mymap.invalidateSize();
//        setTimeout(function() {mymap.invalidateSize()}, 400); // doesn't seem to do anything
    });

    $("#map-col").on('map-container-resize', function () {

    });
});

// query the database to get the factories, buildings, rails, roads. And display them in the map
function loadGeometries(mymap) {
    // get the GeoJSON from the database
    $.getJSON(url_get_factory)
    .done(function (data) {
        L.geoJSON(data, {
            onEachFeature: onEachFeature
        }).addTo(mymap);


    })
    .fail(function (status, err) {
        console.log("Error: Failed to load factories from DB.");
    })
}

// for each factory polygon, get its products
function onEachFeature(feature, layer) {
    if (feature.properties) {
        layer.bindPopup(feature.id + ":" + feature.properties.name);
    }

    layer.on('click', function(e) {
        // bind the feature to its products
        $.getJSON(url_get_factory_products + this.feature.id)
        .done(function (data) {
            for (var i in data) {
                console.log(data[i].properties)
            }
        })
        .fail (function (status, err) {
            console.log("Error: failed to load products from factory", feature.id);
        })
    });
}

//! handler of on the polygon click
function onFeatureClick(feature) {
    alert('click event: ' + feature.id)
}