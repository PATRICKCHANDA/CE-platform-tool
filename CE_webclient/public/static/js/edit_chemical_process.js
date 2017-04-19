$(window).resize(function () {
    // redraw the reaction line when window size changed
    var line = d3.select("#reactionline").select("svg").select("line");
    draw_reactionline(line);
});

function draw_reactionline(a_line) {
    // draw a reaction line
    var svg_width = $("#reactionline").outerWidth();
    var svg_height = 50;//$("#reactionline").outerHeight();
    var svg_container = d3.select("#reactionline").select("svg").attr("width", svg_width);
    var start_x = 5;
    var start_y = 20;
    var end_x = svg_width - 35;
    var end_y = 20;

    a_line.style("stroke", "black")
        .attr("stroke-width", 4)
        .attr("x1", start_x)
        .attr("y1", start_y)
        .attr("x2", end_x)
        .attr("y2", end_y)
        .attr("marker-end", "url(#triangle)");
}


$("button").has("i.fa-plus").on("click", function (e) {
    console.log(e);
});

$("button").has("i.fa-minus").on("click", function (e) {
    console.log(e);
});

$(document).ready(function () {
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
                .style("fill", "black");
    var line = svg_container.append("line");
    draw_reactionline(line);
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