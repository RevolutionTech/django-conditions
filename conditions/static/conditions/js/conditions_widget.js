$(document).ready(function (){
    'use strict'

    // Convert HTML-escaped text to Unicode
    function htmlDecode(input){
        var e = document.createElement('div');
        e.innerHTML = input;
        return e.childNodes[0].nodeValue;
    }

    // Determine category options
    var condition_selector_group_id = 1;
    var condition_selector_id = 1;
    var category_options = "";
    $.each(condition_groups, function(i, val) {
        category_options += "<option value=\"" + val.groupid + "\">" + val.groupname + "</option>";
    });
    category_options += "<option value=\"condlist-all\">New Sublist (all)</option><option value=\"condlist-any\">New Sublist (any)</option>"

    function get_category(row){
        var index = parseInt($('#' + row + '.condition-selector > .condition-groups').val()) - 1;
        return condition_groups[index];
    }
    function get_condition(row){
        var index = parseInt($('#' + row + '.condition-selector > .condstrs').val()) - 1;
        return get_category(row).conditions[index];
    }

    // Add dropdown of condstrs to condition-selector
    function update_condstrs(row, selected_condition){
        // Get condstr options
        var conditions;
        if (selected_condition){
            // Update NOT
            $('#' + row + '.condition-selector > .condition-not').val(selected_condition.bool ? "" : "NOT");
            // Update groups
            $('#' + row + '.condition-selector > .condition-groups').val(selected_condition.groupid);
            conditions = condition_groups[selected_condition.groupid-1].conditions;
        }
        else {
            conditions = get_category(row).conditions;
        }

        // Update condstr options
        var condstrs_options = "";
        $.each(conditions, function(i, val) {
            condstrs_options += "<option value=\"" + val.conditionid + "\">" + val.condstr + "</option>";
        });
        $('#' + row + '.condition-selector > .condstrs').html(condstrs_options);

        // Select condstr
        if (selected_condition){
            $('#' + row + '.condition-selector > .condstrs').val(selected_condition.conditionid);
        }

        // Update key, operator, and operand
        update_condition_key(row, selected_condition);
        update_condition_operators(row, selected_condition);
        define_changes_all();
    }

    // Add dropdown of keys to condition-selector
    function update_condition_key(row, selected_condition){
        var condition = get_condition(row);
        if (condition.key_required){
            if (condition.keys_allowed.length == 0){
                $('#' + row + '.condition-selector > .condition-key').html("<input type=\"text\" placeholder=\"" + condition.key_example + "\" />");

                // Update the selected key
                if (selected_condition){
                    $('#' + row + '.condition-selector > .condition-key > input').val(selected_condition.key);
                }
            }
            else {
                var key_options = "<select>";
                $.each(condition.keys_allowed, function(i, val){
                    key_options += "<option value=\"" + val + "\">" + val + "</option>";
                });
                key_options += "</select>";
                $('#' + row + '.condition-selector > .condition-key').html(key_options);

                // Update the selected key
                if (selected_condition){
                    $('#' + row + '.condition-selector > .condition-key > select').val(selected_condition.key);
                }
            }
        }
        else {
            $('#' + row + '.condition-selector > .condition-key').html("");
        }
    }

    // Add operators and operand to condition-selector
    function update_condition_operators(row, selected_condition){
        var condition = get_condition(row);
        if (condition.operator_required){
            var operator_options = "<select>";
            $.each(condition.operators, function(i, val){
                operator_options += "<option value=\"" + val + "\">" + val + "</option>";
            });
            operator_options += "</select>";
            $('#' + row + '.condition-selector > .condition-operator').html(operator_options);
            $('#' + row + '.condition-selector > .condition-operand').html("<input type=\"text\" placeholder=\"" + condition.operand_example + "\" />");

            // Update the selected operator/operand
            if (selected_condition){
                $('#' + row + '.condition-selector > .condition-operator > select').val(selected_condition.operator);
                $('#' + row + '.condition-selector > .condition-operand > input').val(selected_condition.operand);
            }
        }
        else {
            $('#' + row + '.condition-selector > .condition-operator').html("");
            $('#' + row + '.condition-selector > .condition-operand').html("");
        }
    }

    // Add a new condition selector group when selecting a sublist (or on page load)
    function create_new_condition_selector_group(elementToInsertIn, condlist_type){
        var newid = condition_selector_group_id;
        condition_selector_group_id += 1;
        var new_condition_selector_group = "\
            <div class=\"condition-selector-group\" id=\"" + newid + "\">\
                <select class=\"condition-group-condlist-type\">\
                    <option value=\"condlist-all\" " + (condlist_type == "condlist-all" ? "selected" : "") + ">all</option>\
                    <option value=\"condlist-any\" " + (condlist_type == "condlist-any" ? "selected" : "") + ">any</option>\
                </select>\
                <div class=\"condition-selector-empty\" style=\"margin-left: 10px;\">\
                    <img class=\"condition-add\" src=\"" + staticloc_icon_plus + "\" />\
                </div>\
            </div>";
        elementToInsertIn.html(new_condition_selector_group);

        var newgroup = $('#' + newid + '.condition-selector-group');
        newgroup.find('.condition-selector-empty > .condition-add').click(function() {
            create_new_condition_selector(newid);
            update_json();
        });
        return newgroup;
    }

    // Add a new condition selector with the plus button
    function create_new_condition_selector(group, selected_condition){
        var newid = condition_selector_id;
        condition_selector_id += 1;
        var new_condition_selector = "\
            <div class=\"condition-selector\" style=\"margin-left: 10px;\" id=\"" + newid + "\">\
                <img class=\"condition-remove\" src=\"" + staticloc_icon_minus + "\" />\
                <select class=\"condition-not\">\
                    <option value=\"\"></option>\
                    <option value=\"NOT\">NOT</option>\
                </select>\
                <select class=\"condition-groups\">" + category_options + "</select>\
                <select class=\"condstrs\"></select>\
                <span class=\"condition-key\"></span>\
                <span class=\"condition-operator\"></span>\
                <span class=\"condition-operand\"></span>\
                <img class=\"condition-information\" src=\"" + staticloc_icon_information + "\" />\
            </div>";
        $('#' + group + '.condition-selector-group > .condition-selector-empty').before(new_condition_selector);

        update_condstrs(newid, selected_condition);
        define_changes_row(newid);
    }

    // Update JSON
    function prettifyJSON(text){
        return JSON.stringify(JSON.parse(text), null, '  ');
    }
    function encodeJSON(obj) {
        var first_child = $(obj.children()[0]);
        if (first_child.hasClass('condition-selector-group')){
            var condlist_type = $(first_child.children()[0]).val();
            var condlist_type_text = condlist_type == 'condlist-all' ? "all" : "any";
            var condlist_conditions = first_child.children().slice(1, -1);
            var condlist_json = [];
            $.each(condlist_conditions, function() {
                condlist_json.push(encodeJSON($(this)));
            });
            return "{ \"" + condlist_type_text + "\": [" + condlist_json.join(', ') + "] }";
        }
        else {
            var json;
            // NOT
            var condition_not = obj.find('.condition-not option:selected').text();
            json = condition_not;
            if (condition_not){
                json += " ";
            }

            // CONDSTR
            json += obj.find('.condstrs option:selected').text();

            // KEY
            var key;
            if (obj.find('.condition-key').has('select').length > 0){
                key = obj.find('.condition-key option:selected').text();
            }
            else {
                key = obj.find('.condition-key input').val();
            }
            if (key){
                json += " " + key;
            }

            // OPERATOR
            var operator = obj.find('.condition-operator option:selected').text();
            if (operator){
                json += " " + operator;
            }

            // OPERAND
            if (obj.find('.condition-operand').has('select').length > 0){
                var operand = obj.find('.condition-operand option:selected').text();
            }
            else {
                var operand = obj.find('.condition-operand input').val();
            }
            if (operand){
                json += " " + operand;
            }

            return "\"" + json + "\"";
        }
    }
    function update_json() {
        var json = encodeJSON($('.condition-selector-set'));
        $('.condition-json > textarea').val(prettifyJSON(json));
    }
    function condition_object_from_string(string){
        // NOT
        var bool = true;
        var condition_string = string.split(' ');
        if (condition_string[0] == "NOT"){
            bool = false;
            condition_string = condition_string.slice(1);
        }

        // CONDSTR
        var condstr = condition_string[0];
        condition_string = condition_string.slice(1);

        // Search for the condition object
        var matching_condition_object;
        $.each(condition_groups, function(i, category_object){
            $.each(category_object.conditions, function(i, condition_object){
                if (condition_object.condstr == condstr){
                    matching_condition_object = condition_object;
                    return false;
                }
            });
            if (matching_condition_object) return false;
        });

        // KEY
        var key = "";
        if (matching_condition_object.key_required){
            key = condition_string[0];
            condition_string = condition_string.slice(1);
        }

        // OPERATOR and OPERAND
        var operator = "";
        var operand = "";
        if (matching_condition_object.operator_required){
            operator = condition_string[0];
            operand = condition_string[1];
        }
        return {
            groupid: matching_condition_object.groupid,
            conditionid: matching_condition_object.conditionid,
            bool: bool,
            condstr: condstr,
            keys_allowed: matching_condition_object.keys_allowed,
            key: key,
            operators: matching_condition_object.operators,
            operator: operator,
            operand: operand
        }
    }
    function update_widget_from_json(json, group){
        var condlist_type;
        var conditions;
        if (json.hasOwnProperty('all')){
            condlist_type = 'condlist-all';
            conditions = json['all'];
        }
        else {
            condlist_type = 'condlist-any';
            conditions = json['any'];
        }

        // Create new condition selector group
        var newgroup = create_new_condition_selector_group(group, condlist_type);

        $.each(conditions, function(i, val){
            if ($.type(val) == "string"){
                var selected_condition = condition_object_from_string(val);
                create_new_condition_selector(newgroup.attr('id'), selected_condition);
            }
            else {
                newgroup.find('.condition-selector-empty').before("<div class=\"condition-selector\" style=\"margin-left: 10px;\" id=\"" + condition_selector_id + "\"></div>");
                var condtion_selector = newgroup.find('#' + condition_selector_id + '.condition-selector');
                condition_selector_id += 1;
                update_widget_from_json(val, condtion_selector);
            }
        });
    }
    function update_widget(jsontext) {
        var json = JSON.parse(jsontext);
        update_widget_from_json(json, $('.condition-selector-set'));
    }

    function define_changes_row(row) {
        $('#' + row + '.condition-selector > .condition-groups').change(function() {
            var row = $(this).parent().attr('id');

            var group_choice = $('#' + row + '.condition-selector > .condition-groups').val();
            if (group_choice == "condlist-all" || group_choice == "condlist-any"){
                // Replace the entire row with a new condition selector group, if a condlist type was selected
                create_new_condition_selector_group($('#' + row + '.condition-selector'), group_choice);
            }
            else {
                // Otherwise just update everything else
                update_condstrs(row);
            }
        });
        $('#' + row + '.condition-selector > .condstrs').change(function() {
            var row = $(this).parent().attr('id');
            update_condition_key(row);
            update_condition_operators(row);
            define_changes_all();
        });

        // Show help text when the information icon is clicked
        $('#' + row + '.condition-selector > .condition-information').click(function() {
            var row = $(this).parent().attr('id');
            var condition = get_condition(row);
            var information_text = condition.description;
            if (condition.help_text != condition.description){
                information_text += '\n' + condition.help_text;
            }
            alert(htmlDecode(information_text));
        });

        // Remove the condition selector with the minus button
        $('#' + row + '.condition-selector > .condition-remove').click(function() {
            $(this).parent().remove();
            update_json();
        });

        define_changes_all();
    }

    function define_changes_all(){
        // TODO: Fix so that the change handler does not get set on earlier elements so many times
        $('.condition-selector-set').find('input, select').change(function() {
            update_json();
        });
    }

    // Update conditions widget on JSON update
    $('.condition-json > textarea').change(function(){
        update_widget($(this).val());
    });
    update_widget($('.condition-json > textarea').val());
});
