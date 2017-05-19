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
        zoomOutTitle: '缩小',
        position:'topright'
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
    var info_analysis_col_collapsed = true;
    $("#btn_full_view").on('click', function () {
        info_analysis_col_collapsed = changeLayout(true);
        mymap.invalidateSize();
//        setTimeout(function() {mymap.invalidateSize()}, 400); // doesn't seem to do anything
    });

    $("#btn_scenario_compare").on('click', function () {
        show_scenario_compare(info_analysis_col_collapsed);
        mymap.invalidateSize();
    });

    /* \brief display the name of the product and an input field
    */
    function add_label_and_textfield(div, label_name, chemical_id) {
        var $new_row = $('<div class="row"></div>');
        var label = '<label class="col-sm-6" chemical_id="' + chemical_id + '">' + label_name + ':</label>';
        var textfield = '<input type="text" class="col-sm-4" value=100000>';
        $new_row.append(label);
        $new_row.append(textfield);
        div.append($new_row);
    }

    /*  \brief insert all the process id and names into a drop-down box */
    function display_all_reactions() {
        var $select = $("#all_processes_info .panel-heading > select");
        //    $select.empty();
        $.each(CHEMICAL_PROCESS.get_all_chemical_processes(), function (rf_id, rf_detail) {
            $markup = $("<option value=" + +rf_id + "></option>").text(rf_detail.rf_name);
            $markup.attr("product_ids", rf_detail.product_ids);
            //var markup = '<option value="' + +rf_id + '">' + process_detail.rf_name + '</option>';
            $select.append($markup);
        });
        // todo: draw a chart to show the material input and the products!
    };

    $("#all_processes_info .panel-heading > select").on('change', function (e) {
        $("#info_add_process").text("");
        var $div = $("#process_product_name_quantity");
        // remove all the products info of previous process
        $div.children().remove();
        var product_ids = $("option:selected", this).attr("product_ids").split(',');
        for (var i = 0; i < product_ids.length; ++i) {
            // add the chemical_name and a textarea
            chem_name = CHEMICALS.get_name(product_ids[i]);
            add_label_and_textfield($div, chem_name, product_ids[i]);
        }
    });

    /* \brief btn_add_process_to_factory onclick event: which send the request to server: adding the process into the factory, and
          get response back
    */
    $("#btn_add_process_to_factory").on('click', function (e) {
        // get the process id
        var rf_id = $("#all_processes_info .panel-heading > select").val();
        if (rf_id == null) {
            $("#info_add_process").text('请选择一项工艺');
            return;
        }
        if (g_factory_id == null) {
            $("#info_add_process").text('请点击地图选择企业');
            return;
        }

        var request_content = {};
        // loop through each row with label and input
        $("#process_product_name_quantity").children('div').each(function () {
            var chemical_id = $(this).children('label').attr('chemical_id');
            var volume = $(this).children('input').val();
            request_content[chemical_id] = volume;
        });

        // TODO: post the data to the server!
        // add this reaction_formula into factory
        url = url_insert_rf_to_factory + rf_id + "/" + g_factory_id;
        $.getJSON(url)
        .done(function (data) {
            if (data) {
                if (data.hasOwnProperty('info'))
                    $("#info_add_process").text(data.info);
                else if (data.hasOwnProperty('error'))
                    $("#info_add_process").text(data.error);
                else
                    $("#info_add_process").text("");
                display_factory_processes_info(g_factory_id, data);
                // display
                // show value of the factory
                // show added value of the whole area
                //OVERVIEW.show_area_total_revenue();
            }
        })
        .fail(function (status, err) {
            console.log("Error: failed to add process to factory ", factory_id);
        })
    });

    load_geometries(mymap);
    // load all chemical information
    CHEMICALS.load_all_chemicals(null);
    // load all reaction_formula information
    CHEMICAL_PROCESS.load_all_reactions(display_all_reactions);

    // todo: load the analysis result
    //loadCEAnalysis();

    // todo: whole area revenue
    //OVERVIEW.show_area_total_revenue();
});

//! query the database to get the factories, buildings, rails, roads. And display them in the map
function load_geometries(mymap) {
    // get the GeoJSON from the database
    $.getJSON(url_get_factory)
    .done(function (data) {
        factory_layer = L.geoJSON(data, {
            onEachFeature: on_each_feature
        }).addTo(mymap);
//        mymap.addLayer(factory_layer);

//        markFactoryColor(1);
    })
    .fail(function (status, err) {
        console.log("Error: Failed to load factories from DB.");
    });
}

// for each factory polygon, get its products
function on_each_feature(feature, layer) {
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