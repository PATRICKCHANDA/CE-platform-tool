
$(document).ready(function () {
    $(window).resize(function () {
        // redraw the reaction line when window size changed
        var line = d3.select("#reactionline").select("svg").select("line");
        draw_reactionline(line);
    });
  
    //! add a new table row with 2 columns: <td><input><td> and <td>
    function add_table_row(a_table_body, chem_name, chem_id) {
        var value_cell = '<td><input type="text" value="1" /></td>';
        var name_cell = '<td data_id="'+chem_id+'">' + chem_name +'</td>';
        a_table_body.append('<tr>' + value_cell + name_cell + '</tr>');
    }

    //! draw an arrow line with the specified <div>
    function draw_reactionline(a_line) {
        // draw a reaction line
        var svg_width = $("#reactionline").outerWidth();
        var svg_height = 50;//$("#reactionline").outerHeight();
        var svg_container = d3.select("#reactionline").select("svg").attr("width", svg_width);
        var start_x = 5;
        var start_y = 20;
        var end_x = svg_width - 35;
        var end_y = 20;

        a_line.style("stroke", "red")
            .attr("stroke-width", 4)
            .attr("x1", start_x)
            .attr("y1", start_y)
            .attr("x2", end_x)
            .attr("y2", end_y)
            .attr("marker-end", "url(#triangle)");
    }

    var svg_width = $("#reactionline").outerWidth();
    var svg_height = 50;//$("#reactionline").outerHeight();
    var svg_container = d3.select("#reactionline").select("svg").attr("width", svg_width).attr("height", svg_height);
    svg_container.append("svg:defs").append("svg:marker")
                .attr("id", "triangle")
                .attr("refX", 0)
                .attr("refY", 3)
                .attr("markerWidth", 9)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M 0 0 0 6 9 3")
                .style("fill", "red");
    var line = svg_container.append("line");
    draw_reactionline(line);

    //! fill the chemicals into all <select> elements
    function fill_in_chemicals() {
        $.each(CHEMICALS.get_all_chemicals(), function (id, property) {
            var markup = '<option value="' + +id + '"> ' + property.name + '</option>';
            $('select:not("#processes_list")').append(markup);
        });
    }

    /*  \brief insert all the process id and names into a drop-down box */
    function fill_in_reactions() {
        var $select = $("select#processes_list");
        //    $select.empty();
        $.each(CHEMICAL_PROCESS.get_all_chemical_processes(), function (rf_id, rf_detail) {
            $markup = $("<option value=" + +rf_id + "></option>").text(rf_detail.rf_name);
            $markup.attr("product_ids", rf_detail.product_ids);
            //var markup = '<option value="' + +rf_id + '">' + process_detail.rf_name + '</option>';
            $select.append($markup);
        });
        // todo: draw a chart to show the material input and the products!
    };

    //! load all chemicals
    CHEMICALS.load_all_chemicals(fill_in_chemicals);
    CHEMICAL_PROCESS.load_all_reactions(fill_in_reactions);

    $("select:not('#processes_list')").on({
        "change": function () {
            var $tbl_body = $(this).parent().siblings('table').find('tbody');
            add_table_row($tbl_body, $("option:selected", this).text(), this.value);
            this.blur();
        },
        //// able to select the same item(although no logic in chemical reaction)
        //"focus": function () {
        //    this.selectedIndex = -1;
        //}      
    });

    $("select#processes_list").on({
        "change": function () {
            var $input = $("input#upstream_process_ids");
            var ids = $input.val();
            if (ids == "")
                ids = this.value;
            else
                ids += "," + this.value;
            $input.val(ids);
        }
    });

    //! event handler when click the "+" button: add new row in the table
    $("button").not(".btn-warning").has("i.fa-plus").on("click", function (e) {
        // find the table within the same div as this button
        var $tbl_body = $(this).parent().siblings('table').find('tbody');
        // get the name and id from the select option
        var chem_id = $(this).siblings('select').find('option:selected:enabled').val();
        var chem_name = $(this).siblings('select').find('option:selected:enabled').text();
        if (chem_name != "" && chem_id != undefined)
            add_table_row($tbl_body, chem_name, chem_id);
    });

    //! event handler when click on the "-" button: remove the last row in the table
    $("button").not(".btn-warning").has("i.fa-minus").on("click", function (e) {
        // find the table within the same div as this button
        var $tbl_body = $(this).parent().siblings('table').find('tbody');     
        // remove the last row or the focus row
        //var row_count = $tbl_body.find('tr').length;
        //if (row_count > 2)
        $tbl_body.find("tr:last-child").remove();
    });

    //! plus button for emission table only
    $("button.btn-warning").has("i.fa-plus").on('click', function (e) {
        // find the table within the same div as this button
        var $tbl_body = $(this).parent().siblings('table').find('tbody');
        var name_cell = '<td><input type="text" /></td><td><input type="text" /></td>';
        var value_cells = '<td><input type="number" step="0.0000001" value="0" /></td>' + 
            '<td><input type="number" step="0.0000001" value="0" /></td>' + 
            '<td><input type="number" step="0.0000001" value="0" /></td>' +
            '<td><input type="number" step="0.0000001" value="0" /></td>';
        $tbl_body.append('<tr>' + name_cell + value_cells + '</tr>');
    });
    //! minus button for emission table only
    $("button.btn-warning").has("i.fa-minus").on('click', function (e) {
        // find the table within the same div as this button
        var $tbl_body = $(this).parent().siblings('table').find('tbody');
        //var row_count = $tbl_body.find('tr').length;
        //if (row_count > 1)
        $tbl_body.find("tr:last-child").remove();
    });


    // post the reaction to the server
    $("#send").on("click", function () {
        $("#info_message").text("");
        var request = { reactants: {}, catalysts: {}, products: {}, conditions: {}, emissions: [], utilities: [], upstream_process:""};
        request["description"] = $("input#rf_name").val();
        // read data from the reactants table
        $("#reactant > table > tbody > tr").each(function () {
            var amount = $(this).find("td:eq(0) input").val();
            var chem_id = $(this).find("td:eq(1)").attr("data_id");
            request.reactants[chem_id] = amount; //parseFloat(amount);
        });

        // read data for reaction conditions
        request.conditions["temperature"] = parseFloat($("#reactionT").val());
        request.conditions["pressure"] = parseFloat($("#reactionP").val());
        request.conditions["heat_reaction"] = $("#reactionH").val();
        // read data from catalyst table
        $("#reaction > table > tbody > tr").each(function () {
            var amount = $(this).find("td:eq(0) input").val();
            var chem_id = $(this).find("td:eq(1)").attr("data_id");
            request.catalysts[chem_id] = amount; //parseFloat(amount);
        });
        // read data from products table
        $("#product > table > tbody > tr").each(function () {
            var amount = $(this).find("td:eq(0) input").val();
            var chem_id = $(this).find("td:eq(1)").attr("data_id");
            request.products[chem_id] = amount; //parseFloat(amount);
        });
        // read data from emission table
        $("#emission > table > tbody >tr").each(function () {
            var emission = {};
            emission['name'] = $(this).find("td:eq(0) input").val();
            emission['name_cn'] = $(this).find("td:eq(1) input").val();
            emission['process'] = parseFloat($(this).find("td:eq(2) input").val());
            emission['heat'] = parseFloat($(this).find("td:eq(3) input").val());
            emission['electricity'] = parseFloat($(this).find("td:eq(4) input").val());
            emission['total'] = parseFloat($(this).find("td:eq(5) input").val());
            request.emissions.push(emission);
        });

        // read data for utility information
        $("input[type='checkbox']:checked").each(function () {
            var name = this.value;
            request.utilities.push(name);
        });

        // read data for upstream process
        request.upstream_process = $("input#upstream_process_ids").val();

        // validation
        if (request["description"] == "" || request["description"] == null) {
            $("#info_message").text("Error: Missing description.");
            return;
        }
        if (jQuery.isEmptyObject(request.reactants)) {
            $("#info_message").text("Error: No reactants defined.");
            return;
        }
        if (jQuery.isEmptyObject(request.products)) {
            $("#info_message").text("Error: No products defined.");
            return;
        }

        // post the data to server
        $.ajax({
            type: "POST",
            url: url_post_reaction_formula,
            data: JSON.stringify(request),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8'
        })
        .done(function (data) {
            $("#info_message > i").addClass("fa-smile-o");
            $("#info_message").text("提交成功(succeed)");
        })
        .fail(function (err) {
            $("#info_message").text(data.msg);
        })
    });
});