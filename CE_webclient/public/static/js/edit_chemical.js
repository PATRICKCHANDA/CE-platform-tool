$(document).ready(function () {
    function fill_in_chemicals() {
        $.each(CHEMICALS.get_all_chemicals(), function (id, property) {
            var markup = '<option value="' + +id + '"> ' + property.name + '</option>';
            $('select#chemical_list').append(markup);
        });
    }

    //! fill in the select with all chemicals
    CHEMICALS.load_all_chemicals(fill_in_chemicals);

    // chemical list change event handler
    $("#chemical_list").on('change', function () {        
        if ($("option:selected", this).text() == "" || this.value == "") {
            // in insert mode:　change the button name, enable the fields
            $('#send').text("Insert");
            $("#chemical_detail fieldset").prop("disabled", false);
        }
        else {
            // in update mode: disable some fields, and rename the button
            $('#send').text("Update");
            $("#chemical_detail fieldset").prop("disabled", true);

        }
    });

    // sumbit the change/new
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
                min: "单位成本必须大于0"
            },
            unit_transport_cost: {
                min: "单位成本必须大于0"
            },
            sp_heat: {
                min:"必须大于0"
            }
        },
        submitHandler:function(form) {
            $.ajax({
                url: 'some-url',
                type: 'post',
                dataType: 'json',
                data: $('#chemical_detail').serialize(),
                success: function (data) {
                    // fill in the dropdown box again
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

    $("#reset").on("click", function () {
        var form = $("#chemical_detail");
        form.validate().resetForm();      // clear out the validation errors
        form[0].reset();
    });
})