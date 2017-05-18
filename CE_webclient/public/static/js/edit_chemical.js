$(document).ready(function () {
    function fill_in_chemicals() {
        $.each(CHEMICALS.get_all_chemicals(), function (id, property) {
            var markup = '<option value="' + +id + '"> ' + property.name + '</option>';
            $('select#chemical_list').append(markup);
        });
    }

    //! load all the chemicals from db and fill in the dropdown list
    CHEMICALS.load_all_chemicals(fill_in_chemicals);
    //console.log($("input").length);
    // chemical list change event handler
    $("#chemical_list").on('change', function () {
        var form = $("#chemical_detail");
        form.validate().resetForm();      // clear out the validation errors
        $("#info_message").html("");
        //console.log($("input").length);

        // if nothing selected from the dropdown list: it is in insert mode, otherwise update mode
        if ($("option:selected", this).text() == "" || this.value == "") {
            // in insert mode:　reset all the form fields, 
            // reset values to default
            $("input").each(function () {
                $(this).val(this.defaultValue);
            });
            // change the button name, enable the fields
            $('#send').text("Insert");
            $("#chemical_detail fieldset").prop("disabled", false);
        }
        else {
            // in update mode: fill in the fields, then disable some fields for editing, and rename the button
            var chemical_detail = CHEMICALS.get_a_chemical(+this.value);
            $('input#cname_en').val(chemical_detail.name_en);
            $('input#cname_cn').val(chemical_detail.name_cn);
            $('input#cmolar_mass').val(chemical_detail.molar_mass);
            $('input#cdensity').val(chemical_detail.density);
            $('input#csymbol').val(chemical_detail.symbol);
            $('select#cunit option').each(function () {
                this.selected = (this.value.toUpperCase() === chemical_detail.unit.toUpperCase())
            });
            $('input#cunit_cost').val(chemical_detail.value_per_unit);
            $('input#cunit_transport_cost').val(chemical_detail.unit_transport_cost);
            $('select#ccurrency option').each(function () {
                this.selected = (this.value.toUpperCase() === chemical_detail.currency.toUpperCase())
            });
            $('input#csp_heat').val(chemical_detail.sp_heat);
            // rename the button
            $('#send').text("Update");
            // disable some fields for editing
            $("#chemical_detail fieldset").prop("disabled", true);
            //console.log($("input").length);
        }
    });

    // submit the change/new
    $("#chemical_detail").validate({
        //errorPlacement: function (label, element) {
        //    label.addClass('error help-inline');
        //    label.insertAfter(element);
        //},
        focusCleanup: true,
        rules: {
            name_en: {
                minlength: 2,
                required: true
            },
            name_cn: {
                required: true,
            },
            molar_mass: {
                required: true,
                min:1
            },
            density: {
                required: true,
                min: 0
            },
            symbol: "required",
            unit_cost: {
                required:true,
                min:0
            },
            unit_transport_cost: {
                min:0
            },
            sp_heat: {
                min:0
            }
        },
        messages: {
            name_en: " 请输入英文名",
            name_cn: " 请输入中文名",
            molar_mass: {
                required: " 请输入分子量",
            },
            density: {
                required: " 请输入密度",
                min: "密度必须大于0"
            },
            symbol: " 请输入分子式",
            unit_cost: {
                required: "请输入单位价值",
                min: "单位价值必须大于0"
            },
            unit_transport_cost: {
                min: "单位运输成本必须大于0"
            },
            sp_heat: {
                min:"必须大于0"
            }
        },
        submitHandler: function (form) {
            var request = {};
            // get the chemical id
            var chem_id = $("#chemical_list option:selected").val();
            var insert_mode = false;
            if (chem_id == null || chem_id == "") {// insert mode
                request["chem_id"] = null;
                insert_mode = true;
            }
            else
                request["chem_id"] = chem_id;

            // get all input field value
            console.log($("input").length);
            console.log($("form#chemical_detail input").length);
            $("form#chemical_detail input").each(function () {
                var name = $(this).attr("name");
                var value = $(this).val();
                if (name != "")
                    request[name] = value;
            });
            // get dropdown list value
            $("form#chemical_detail select").each(function () {
                var name = $(this).attr("name");
                var value = $("option:selected", this).val();
                request[name] = value;
            });

            $.ajax({
                url: url_post_chemical,
                type: 'post',
                dataType: 'json',
                data: JSON.stringify(request),
                contentType: 'application/json; charset=utf-8',
                success: function (data) {
                    $("#info_message").html(data.msg);
                    //console.log(data.msg);
                }
            });
        },
        invalidHandler: function (event, validator) {
            // 'this' refers to the form
            var errors = validator.numberOfInvalids();
            if (errors) {
                var message = errors == 1
                  ? 'You missed 1 field.' // help-inline
                  : 'You missed ' + errors + ' fields.'; //  They have been highlighted
                $("#info_message").html(message);
                $("#info_message").show();
            }
            else {
                $("#info_message").html("");
            }
        }
    });

    //! reset button onclick event handler
    $("#reset").on("click", function () {
        var form = $("#chemical_detail");
        form.validate().resetForm();      // clear out the validation errors
//        form[0].reset();
        $("#info_message").html("");
        $("#chemical_list").prop("selectedIndex", 0);
    });
})