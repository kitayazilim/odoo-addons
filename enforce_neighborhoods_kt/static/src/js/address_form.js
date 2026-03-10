odoo.define('enforce_neighborhoods_kt.address_form', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var websiteSale = require('website_city_selection.city_selection');

    publicWidget.registry.WebsiteSale.include({
        /**
         * @override
         */
        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
            'change select[name="city_id"]': '_onChangeCity',

        }),

        /**
     * @constructor
     */
        init: function () {
            this._super.apply(this, arguments);
            this._onChangeCity = _.debounce(this._changeCity.bind(this), 500);
        },

        _changeCountry: async function () {
            const res = await this._super.apply(this, arguments);
            // Check if res is defined and has the neighborhood_required property
            if (res && 'neighborhood_required' in res && res.neighborhood_required) {
                $("select[name='neighborhood_kt_id']").show();
                $("label[for='neighborhood_kt_id']").css('display', 'block');
            } else {
                $("select[name='neighborhood_kt_id']").hide();
                $("label[for='neighborhood_kt_id']").css('display', 'none');
            }
        },

        _changeCity: function (ev) {
            var cityID = $(ev.currentTarget).val();
            if (!cityID) {
                return;
            }

            var countryID = this.$('select[name="country_id"]').val();
            if (!countryID) {
                return;
            }

            var self = this;
            var neighborhoodSelect = this.$('select[name="neighborhood_kt_id"]');
            self._loadNeighborhoods(cityID, neighborhoodSelect);

        },

        _loadNeighborhoods: function(cityID, neighborhoodSelect) {
            this._rpc({
                route: '/shop/neighborhoods_kt',
                params: {
                    city_id: cityID
                },
            }).then(function (data) {
                if (neighborhoodSelect.data('init') === 0 || neighborhoodSelect.find('option').length === 1) {
                    if (data && data.length) {
                        neighborhoodSelect.html('<option value=""></option>');
                        _.each(data, function (neighborhood) {
                            neighborhoodSelect.append($('<option>', {
                                value: neighborhood[0],
                                text: neighborhood[1]
                            }));
                        });
                    }
                    neighborhoodSelect.data('init', 0);
                }else {
                    neighborhoodSelect.data('init', 0);
                }
            });
        }

    });

});