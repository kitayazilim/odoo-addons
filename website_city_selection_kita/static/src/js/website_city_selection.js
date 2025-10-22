odoo.define('website_city_selection_kita.city_selection', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var websiteSale = require('website_sale.website_sale');

publicWidget.registry.WebsiteSale.include({
    /**
     * @override
     */
    events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
        'change select[name="state_id"]': '_onChangeState',
    }),

    /**
 * @constructor
 */
    init: function () {
        this._super.apply(this, arguments);
        this._onChangeState = _.debounce(this._changeState.bind(this), 500);
    },

    /**
     * @override
     * we override becauser of not return promise
     * @returns {Object} data
     */
    _changeCountry: async function () {
        if (!$("#country_id").val()) {
            return;
        }
        const data = await this._rpc({
            route: "/shop/country_infos/" + $("#country_id").val(),
            params: {
                mode: $("#country_id").attr('mode'),
            },
        })
        // placeholder phone_code
        $("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

        if (data.enforce_cities) {
            $("select[name='city_id']").show();
            $("input[name='city']").hide();
        }else{
            $("input[name='city']").show();
            $("select[name='city_id']").hide();
        }

        // populate states and display
        var selectStates = $("select[name='state_id']");
        // dont reload state at first loading (done in qweb)
        if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
            if (data.states.length || data.state_required) {
                selectStates.html('<option value=""></option>');
                _.each(data.states, function (x) {
                    var opt = $('<option>').text(x[1])
                        .attr('value', x[0])
                        .attr('data-code', x[2]);
                    selectStates.append(opt);
                });
                selectStates.parent('div').show();
            } else {
                selectStates.val('').parent('div').hide();
            }
            selectStates.data('init', 0);
        } else {
            selectStates.data('init', 0);
        }

        // manage fields order / visibility
        if (data.fields) {
            if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
                $(".div_zip").before($(".div_city"));
            } else {
                $(".div_zip").after($(".div_city"));
            }
            var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
            _.each(all_fields, function (field) {
                $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
            });
        }

        if ($("label[for='zip']").length) {
            $("label[for='zip']").toggleClass('label-optional', !data.zip_required);
            $("label[for='zip']").get(0).toggleAttribute('required', !!data.zip_required);
        }
        if ($("label[for='zip']").length) {
            $("label[for='state_id']").toggleClass('label-optional', !data.state_required);
            $("label[for='state_id']").get(0).toggleAttribute('required', !!data.state_required);
        }
        return data
    },


    /**
     * @private
     * @param {Event} ev
     */
    _changeState: function (ev) {
        // if (!this.$('.checkout_autoformat').length) {
        //     return;
        // }
        var stateID = $("select[name='state_id']").val();
        if (stateID) {
            this._loadCities(stateID);
        } else {
            // Clear city dropdown when state is not selected
            $("select[name='city_id']").html('<option value=""></option>');
        }
    },

    /**
     * @private
     * @param {Number} stateID
     */
    _loadCities: function (stateID) {
        this._rpc({
            route: "/shop/state_infos/" + stateID,
            params: {},
        }).then(function (data) {
            var selectCity = $("select[name='city_id']");
            // Don't reload cities at first loading (done in qweb)
            if (selectCity.data('init') === 0 || selectCity.find('option').length === 1) {
                if (data.cities && data.cities.length) {
                    selectCity.html('<option value=""></option>');
                    _.each(data.cities, function (x) {
                        var opt = $('<option>').text(x[1])
                            .attr('value', x[0]);
                        selectCity.append(opt);
                    });
                }
                selectCity.data('init', 0);
            }else {
                selectCity.data('init', 0);
            }
        });
    }
});

});
