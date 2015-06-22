$(function(){
    'use strict'

    // Convert HTML-escaped text to Unicode
    function htmlDecode(input){
        var e = document.createElement('div');
        e.innerHTML = input;
        return e.childNodes[0].nodeValue;
    }
    // JSON
    function prettifyJSON(text){
        return JSON.stringify(text, null, '  ');
    }

    var ConditionList = Backbone.Model.extend();
    var ConditionNot = Backbone.Model.extend();
    var ConditionGroup = Backbone.Model.extend();
    var Condstr = Backbone.Model.extend();
    var ConditionKey = Backbone.Model.extend();
    var ConditionOperator = Backbone.Model.extend();

    var condition_group_list = $.merge(
        $.map(condition_groups, function(val){
            return new ConditionGroup({
                id: val.groupid,
                name: val.groupname,
                conditions: $.map(val.conditions, function(val){
                    return new Condstr({
                        id: val.condstr,
                        name: val.condstr,
                        key_required: val.key_required,
                        keys_allowed: $.map(val.keys_allowed, function(val){
                            return new ConditionKey({
                                id: val,
                                name: val
                            });
                        }),
                        key_example: val.key_example,
                        operator_required: val.operator_required,
                        operators: $.map(val.operators, function(val){
                            return new ConditionOperator({
                                id: val,
                                name: val
                            });
                        }),
                        operand_example: val.operand_example,
                        help_text: val.help_text,
                        description: val.description
                    });
                }),
            });
        }),
        [
            new ConditionList({id: "all", name: "New sublist (all)"}),
            new ConditionList({id: "any", name: "New sublist (any)"})
        ]
    );

    var SelectListView = Backbone.View.extend({
        defaults: {
            show: true,
            options: []
        },
        initialize: function(){
            this.render();
            this.current_selection = $(this.el).children().first().val();
        },
        render: function(){
            var template = "";
            if (this.options.show) template = _.template($('#select-list-template').html(), {options: this.options.options});
            this.$el.html(template);
        },
        events: {
            "change": "changeSelected"
        },
        changeSelected: function(){
            this.current_selection = $(this.el).children().first().val();
            this.setSelectedId(this.current_selection);

            // Update JSON
            this.condition_selector_view.updateJSON();
        },
        setSelectedId: function(id){
            // do nothing by default
        }
    });
    var InputView = Backbone.View.extend({
        defaults: {
            show: true,
            placeholder: ""
        },
        initialize: function(){
            this.render();
            this.current_selection = $(this.$el).children().val();
        },
        render: function(){
            var template = "";
            if (this.options.show) template = _.template($('#input-template').html(), {placeholder: this.options.placeholder});
            this.$el.html(template);
        },
        events: {
            "change": "changeInput"
        },
        changeInput: function(){
            this.current_selection = $(this.el).children().val();

            // Update JSON
            this.condition_selector_view.updateJSON();
        }
    });
    var SelectOrInputView = SelectListView.extend({
        defaults: {
            show: true,
            options: [],
            placeholder: ""
        },
        render: function(){
            var template;

            // Show select if we have options, otherwise an open input field
            if (this.options.show && this.options.options.length > 0){
                template = _.template($('#select-list-template').html(), {options: this.options.options});
            }
            else if (this.options.show) {
                template = _.template($('#input-template').html(), {placeholder: this.options.placeholder});
            }
            else {
                template = "";
            }

            this.$el.html(template);
        },
        changeSelected: function(){
            if (this.options.options.length > 0){
                this.current_selection = $(this.el).children().first().val();
                this.setSelectedId(this.current_selection);
            }
            else {
                this.current_selection = $(this.el).children().val();
            }

            // Update JSON
            this.condition_selector_view.updateJSON();
        }
    })

    var ConditionGroupListView = SelectListView.extend({
        setSelectedId: function(groupid){
            // Handle sub-condlist
            if (groupid == "all" || groupid == "any"){
                var condition_selector_group_view = new ConditionSelectorGroupView({
                    el: $(this.el).parent(),
                    listtype: groupid
                });
                this.condition_selector_view.condition_selector_child_group = condition_selector_group_view;
                condition_selector_group_view.condition_selector_parent_group = this.condition_selector_view.condition_selector_group;
            }
            else {
                this.condstr_list_view.options.options = condition_group_list[groupid-1].get('conditions');
                this.condstr_list_view.render();
                this.condstr_list_view.changeSelected();
            }

            // Update JSON
            this.condition_selector_view.updateJSON();
        }
    });
    var CondstrListView = SelectListView.extend({
        setSelectedId: function(conditionid){
            // Get condition from id
            var index = -1;
            $.each(this.options.options, function(i, val){
                if (val.get('name') == conditionid) {
                    index = i;
                    return;
                }
            })
            var condition = this.options.options[index];

            // Update and render condition key input view
            this.condition_key_input_view.options.show = condition.get('key_required');
            this.condition_key_input_view.options.options = condition.get('keys_allowed');
            this.condition_key_input_view.options.placeholder = condition.get('key_example');
            this.condition_key_input_view.render();
            this.condition_key_input_view.changeSelected();

            // Update and render condition operators and operand
            this.condition_operator_list_view.options.show = condition.get('operator_required');
            this.condition_operator_list_view.options.options = condition.get('operators');
            this.condition_operator_list_view.render();
            this.condition_operator_list_view.changeSelected();
            this.condition_operand_input_view.options.show = condition.get('operator_required');
            this.condition_operand_input_view.options.placeholder = condition.get('operand_example');
            this.condition_operand_input_view.render();
            this.condition_operand_input_view.changeInput();

            // Update condition selector
            this.condition_selector_view.selected_condition = condition;

            // Update JSON
            this.condition_selector_view.updateJSON();
        }
    });

    var ConditionSelectorView = Backbone.View.extend({
        initialize: function(){
            // Render empty condition selector
            this.render();

            // Get default condition
            var condition_groups = this.options.condition_groups;
            var selected_condition_list = condition_groups[0].get('conditions');
            var selected_condition = selected_condition_list[0];
            this.selected_condition = selected_condition;

            // Create components of condition selector
            // NOT
            this.condition_not_list_view = new SelectListView({
                el: $(this.el).find('#condition-not'),
                show: true,
                options: [new ConditionNot({id: "", name: ""}), new ConditionNot({id: "NOT", name: "NOT"})]
            });
            this.condition_not_list_view.condition_selector_view = this;

            // Group
            this.condition_group_list_view = new ConditionGroupListView({
                el: $(this.el).find('#condition-groups'),
                show: true,
                options: condition_groups
            });
            this.condition_group_list_view.condition_selector_view = this;

            // CONDSTR
            this.condstr_list_view = new CondstrListView({
                el: $(this.el).find('#condstrs'),
                show: true,
                options: selected_condition_list
            });
            this.condition_group_list_view.condstr_list_view = this.condstr_list_view;
            this.condstr_list_view.condition_selector_view = this;

            // KEY
            this.condition_key_input_view = new SelectOrInputView({
                el: $(this.el).find('#condition-key'),
                show: selected_condition.get('key_required'),
                options: selected_condition.get('keys_allowed'),
                placeholder: selected_condition.get('key_example')
            });
            this.condstr_list_view.condition_key_input_view = this.condition_key_input_view;
            this.condition_key_input_view.condition_selector_view = this;

            // OPERATOR
            this.condition_operator_list_view = new SelectListView({
                el: $(this.el).find('#condition-operators'),
                show: selected_condition.get('operator_required'),
                options: selected_condition.get('operators')
            });
            this.condstr_list_view.condition_operator_list_view = this.condition_operator_list_view;
            this.condition_operator_list_view.condition_selector_view = this;

            // OPERAND
            this.condition_operand_input_view = new InputView({
                el: $(this.el).find('#condition-operand'),
                show: selected_condition.get('operator_required'),
                placeholder: selected_condition.get('operand_example')
            });
            this.condstr_list_view.condition_operand_input_view = this.condition_operand_input_view;
            this.condition_operand_input_view.condition_selector_view = this;
        },
        render: function(){
            var template = _.template($('#condition-selector-template').html(), {});
            this.$el.html(template);
        },
        events: {
            'click img#condition-remove': 'removeself',
            'click img#condition-information': 'information'
        },
        updateJSON: function(){
            this.condition_selector_group.updateJSON();
        },
        encodeJSON: function(){
            // If sublist, encode that JSON
            if (this.condition_selector_child_group) return this.condition_selector_child_group.encodeJSON();

            var a = [];

            // NOT
            var condition_not_selection = this.condition_not_list_view.current_selection;
            if (condition_not_selection != "") a.push(condition_not_selection);

            // CONDSTR
            a.push(this.condstr_list_view.current_selection);

            // KEY
            if (this.selected_condition.get('key_required')) a.push(this.condition_key_input_view.current_selection);

            // OPERATOR and OPERAND
            if (this.selected_condition.get('operator_required')){
                a.push(this.condition_operator_list_view.current_selection);
                a.push(this.condition_operand_input_view.current_selection);
            }

            return a.join(" ");
        },
        removeself: function(e){
            e.stopImmediatePropagation(); // do not propagate to parents

            // Remove from group selections
            var self = this;
            $.each(this.condition_selector_group.condition_selectors, function(i, val){
                if (self === val){
                    self.condition_selector_group.condition_selectors.splice(i, 1);
                    return false;
                }
            });

            // Update JSON
            this.condition_selector_group.updateJSON();

            // Remove
            this.condition_selector_group.remove_group_if_empty();
            this.remove();
        },
        information: function(e){
            e.stopImmediatePropagation(); // do not propagate to parents

            var information_text = this.selected_condition.get('description');
            if (this.selected_condition.get('help_text') != information_text){
                information_text += '\n' + this.selected_condition.get('help_text');
            }
            alert(htmlDecode(information_text));
        }
    });

    var ConditionSelectorGroupView = Backbone.View.extend({
        defaults: {
            listtype: "all"
        },
        initialize: function(){
            this.render();

            // Create initial condition selector
            var condition_selector_view = new ConditionSelectorView({
                el: $(this.el).find('#condition-selector-group > #condition-selector'),
                condition_groups: condition_group_list
            });
            this.condition_selectors = [condition_selector_view];
            condition_selector_view.condition_selector_group = this;
        },
        render: function(){
            var template = _.template($('#condition-selector-group-template').html(), {listtype: this.options.listtype});
            this.$el.html(template);
        },
        events: {
            'change': 'changeSelected',
            'click img#condition-add': 'add_condition'
        },
        changeSelected: function(){
            this.options.listtype = $(this.el).find('#condition-selector > select').val();

            // Update JSON
            this.updateJSON();
        },
        encodeJSON: function(){
            var d = {}
            d[this.options.listtype] = $.map(this.condition_selectors, function(val){
                return val.encodeJSON();
            });
            return d;
        },
        updateJSON: function(){
            if (this.condition_selector_parent_group){
                return this.condition_selector_parent_group.updateJSON();
            }

            $('#condition-json > textarea').val(prettifyJSON(this.encodeJSON()));
        },
        remove_group_if_empty: function(){
            if ($(this.el).find('#condition-selector-group').first().children().length <= 1){
                if (this.condition_selector_parent_group){ // do not remove if this is the root
                    this.condition_selector_parent_group.remove_group_if_empty();

                    // Remove self from group selectors
                    var self = this;
                    $.each(this.condition_selector_parent_group.condition_selectors, function(i, val){
                        if (self === val.condition_selector_child_group){
                            self.condition_selector_parent_group.condition_selectors.splice(i, 1);
                            return false;
                        }
                    });

                    // Update JSON and remove self
                    this.updateJSON();
                    this.remove();
                }
            }
        },
        add_condition: function(e){
            e.stopImmediatePropagation(); // do not propagate to parents

            $(this.el).children().children('#condition-selector-group').append("<div style=\"margin-left: 10px;\" id=\"condition-selector\"></div>");
            var condition_selector_view = new ConditionSelectorView({
                el: $(this.el).find('#condition-selector-group > #condition-selector').last(),
                condition_groups: condition_group_list
            });
            this.condition_selectors.push(condition_selector_view);
            condition_selector_view.condition_selector_group = this;

            this.updateJSON();
        }
    });
    var condition_selector_group_view = new ConditionSelectorGroupView({
        el: $('#condition-selector-widget'),
        listtype: "all"
    });

});
