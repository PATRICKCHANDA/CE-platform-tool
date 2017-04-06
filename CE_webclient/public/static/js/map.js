var custom_bounds = new L.LatLngBounds(
    new L.LatLng(21.9, 113.12),
    new L.LatLng(22.000000, 113.3));

var mymap = L.map('map-col', { zoomControl: false}).fitBounds(custom_bounds);
var factory_layer;  // geojson layer containing all the factories

$(document).ready(function () {
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
    $("#btn_full_view").on('click', function() {
        changeLayout(true);
        mymap.invalidateSize();
//        setTimeout(function() {mymap.invalidateSize()}, 400); // doesn't seem to do anything
    });

    loadGeometries(mymap);
    // todo: load all chemical information
    loadAllChemicals();
    // Todo: load all reaction_formula information
    loadAllReactions();
    // todo: load the analysis result
    //loadCEAnalysis();

    // todo: whole area revenue
    OVERVIEW.show_area_total_revenue();
});

function loadAllReactions() {
    $.getJSON(url_get_reactions)
    .done(function (data) {
        if (data.length > 0)
            display_all_reactions(data);
    })
    .fail(function (status, err) {
        console.log("Error: Failed to load reactions from DB.");
    })
}

function loadAllChemicals() {
    $.getJSON(url_get_chemicals)
    .done(function (data) {
        if (data.length > 0)
            CHEMICALS.display_all_chemicals(data);
    })
    .fail(function (status, err) {
        console.log("Error: Failed to load chemicals from DB.");
    })
}
// query the database to get the factories, buildings, rails, roads. And display them in the map
function loadGeometries(mymap) {
    // get the GeoJSON from the database
    $.getJSON(url_get_factory)
    .done(function (data) {
        factory_layer = L.geoJSON(data, {
            onEachFeature: onEachFeature
        }).addTo(mymap);
//        mymap.addLayer(factory_layer);

//        markFactoryColor(1);
    })
    .fail(function (status, err) {
        console.log("Error: Failed to load factories from DB.");
    });
}

// for each factory polygon, get its products
function onEachFeature(feature, layer) {
    // show the clicked feature name
    if (feature.properties) {
        layer.bindPopup(feature.id + ":" + feature.properties.name);
    }

    layer.on('click', function(e) {
        changeLayout(false);
        mymap.invalidateSize();
        // bind the feature to its products
        factory_id = this.feature.id;
        $.getJSON(url_get_factory_products + factory_id)
        .done(function (data) {
            if (data.length > 0)
                console.log(data[0].rf_name)
            display_factory_processes_info(factory_id, data);
        })
        .fail (function (status, err) {
            console.log("Error: failed to load products from factory", feature.id);
        })
        resetFactoryColor();
    });
}

//! handler of on the polygon click
function onFeatureClick(feature) {
    alert('click event: ' + feature.id)
}

function markFactoryColor(factory_id) {
    factory_layer.eachLayer(function (layer) {
        if (layer.feature.id == factory_id) {
            layer.setStyle({fillColor:'#fff460', fillOpacity:1.0});
        };
    });
}

function resetFactoryColor(factory_id) {
    factory_layer.eachLayer(function (layer) {
        if (layer.feature.id == factory_id) {
            factory_layer.resetStyle(layer);
            return;
        };
    });
}

function resetFactoryColor() {
    factory_layer.eachLayer(function (layer) {
        factory_layer.resetStyle(layer);
    });
}