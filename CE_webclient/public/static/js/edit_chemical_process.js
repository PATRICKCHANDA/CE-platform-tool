
$(document).ready(function () {
    $(window).resize(function () {
        // redraw the reaction line when window size changed
        var line = d3.select("#reactionline").select("svg").select("line");
        draw_reactionline(line);
    });
  
    //! add a new table row with 2 columns: <td><input><td> and <td>
    function add_table_row(a_table_body, chem_name, chem_id) {
        var value_cell = '<td><input type="number" step="0.0001" value="1" /></td>';
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

    function fill_in_chemicals() {
        $.each(CHEMICALS.get_all_chemicals(), function (id, property) {
            var markup = '<option value="' + +id + '"> ' + property.name + '</option>';
            $('select').append(markup);
        });
    }
    //! fill in the select with all chemicals
    CHEMICALS.load_all_chemicals(fill_in_chemicals);

    $("select").on({
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

    //! event handler when click the "+" button: add new row in the table
    $("button").has("i.fa-plus").on("click", function (e) {
        // add a new row in the table
        // find the table within the same div as this button
        var $tbl_body = $(this).parent().siblings('table').find('tbody');
        // get the name and id from the select option
        var chem_id = $(this).siblings('select').find('option:selected:enabled').val();
        var chem_name = $(this).siblings('select').find('option:selected:enabled').text();
        if (chem_name != "" && chem_id != undefined)
            add_table_row($tbl_body, chem_name, chem_id);
    });

    //! event handler when click on the "-" button: remove the last row in the table
    $("button").has("i.fa-minus").on("click", function (e) {
        // find the table within the same div as this button
        var $tbl_body = $(this).parent().siblings('table').find('tbody');     
        // remove the last row or the focus row
        $tbl_body.find("tr:last-child").remove();
    });

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

    $("#send").on("click", function () {
        var request = { reactants: {}, catalysts: {}, products: {}, conditions: {}};

        // read data from the reactants table
        $("#reactant > table > tbody > tr").each(function () {
            var amount = $(this).find("td:eq(0) input").val();
            var chem_id = $(this).find("td:eq(1)").attr("data_id");
            request.reactants[chem_id] = parseFloat(amount);
        });
        request.conditions["temperature"] = parseFloat($("#reactionT").val());
        request.conditions["pressure"] = parseFloat($("#reactionP").val());
        // read data from catalyst table
        $("#reaction > table > tbody > tr").each(function () {
            var amount = $(this).find("td:eq(0) input").val();
            var chem_id = $(this).find("td:eq(1)").attr("data_id");
            request.catalysts[chem_id] = parseFloat(amount);
        });
        // read data from products table
        $("#product > table > tbody > tr").each(function () {
            var amount = $(this).find("td:eq(0) input").val();
            var chem_id = $(this).find("td:eq(1)").attr("data_id");
            request.products[chem_id] = parseFloat(amount);
        });

        // todo: post the data to server
        $.ajax({
            type: "POST",
            url: url_post_reaction_formula,
            data: JSON.stringify(request),
            dataType: 'json',
            contentType: 'application/json; charset=utf-8'
        })
        .done(function (data) {
            $("#info_message > i").addClass("fa-smile-o");
            $("#info_message > i").text(" " + data.msg);
        })
        .fail(function (err) {
            $("#info_message").text("Oops!Failed.");
        })
    });
    //$('#contact_form').bootstrapValidator({
    //    // To use feedback icons, ensure that you use Bootstrap v3.1.0 or later
    //    feedbackIcons: {
    //        valid: 'glyphicon glyphicon-ok',
    //        invalid: 'glyphicon glyphicon-remove',
    //        validating: 'glyphicon glyphicon-refresh'
    //    },
    //    fields: {
    //        first_name: {
    //            validators: {
    //                stringLength: {
    //                    min: 2,
    //                },
    //                notEmpty: {
    //                    message: 'Please supply your first name'
    //                }
    //            }
    //        },
    //        last_name: {
    //            validators: {
    //                stringLength: {
    //                    min: 2,
    //                },
    //                notEmpty: {
    //                    message: 'Please supply your last name'
    //                }
    //            }
    //        },
    //        email: {
    //            validators: {
    //                notEmpty: {
    //                    message: 'Please supply your email address'
    //                },
    //                emailAddress: {
    //                    message: 'Please supply a valid email address'
    //                }
    //            }
    //        },
    //        phone: {
    //            validators: {
    //                notEmpty: {
    //                    message: 'Please supply your phone number'
    //                },
    //                phone: {
    //                    country: 'US',
    //                    message: 'Please supply a vaild phone number with area code'
    //                }
    //            }
    //        },
    //        address: {
    //            validators: {
    //                stringLength: {
    //                    min: 8,
    //                },
    //                notEmpty: {
    //                    message: 'Please supply your street address'
    //                }
    //            }
    //        },
    //        city: {
    //            validators: {
    //                stringLength: {
    //                    min: 4,
    //                },
    //                notEmpty: {
    //                    message: 'Please supply your city'
    //                }
    //            }
    //        },
    //        state: {
    //            validators: {
    //                notEmpty: {
    //                    message: 'Please select your state'
    //                }
    //            }
    //        },
    //        zip: {
    //            validators: {
    //                notEmpty: {
    //                    message: 'Please supply your zip code'
    //                },
    //                zipCode: {
    //                    country: 'US',
    //                    message: 'Please supply a vaild zip code'
    //                }
    //            }
    //        },
    //        comment: {
    //            validators: {
    //                stringLength: {
    //                    min: 10,
    //                    max: 200,
    //                    message: 'Please enter at least 10 characters and no more than 200'
    //                },
    //                notEmpty: {
    //                    message: 'Please supply a description of your project'
    //                }
    //            }
    //        }
    //    }
    //})
    //    .on('success.form.bv', function (e) {
    //        $('#success_message').slideDown({ opacity: "show" }, "slow") // Do something ...
    //        $('#contact_form').data('bootstrapValidator').resetForm();

    //        // Prevent form submission
    //        e.preventDefault();

    //        // Get the form instance
    //        var $form = $(e.target);

    //        // Get the BootstrapValidator instance
    //        var bv = $form.data('bootstrapValidator');

    //        // Use Ajax to submit form data
    //        $.post($form.attr('action'), $form.serialize(), function (result) {
    //            console.log(result);
    //        }, 'json');
    //    });
});