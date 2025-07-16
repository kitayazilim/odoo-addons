odoo.define('payment_paytr_kt.payment_form', require => {
    'use strict';

    const core = require('web.core');
    const { loadJS } = require('@web/core/assets');
    const checkoutForm = require('payment.checkout_form');

    const _t = core._t;

    const paytrMixin = {

        async _processDirectPayment(code, providerId, processingValues) {
            if (code !== 'paytr') {
                return this._super(...arguments);
            }

            const res_json = await this._rpc({
                route: '/payment/paytr/get-iframe-token',
                params: {
                    'reference': processingValues.reference,
                    'providerId': providerId
                },
            })
            this._enableButton();
            $('body').unblock();
            document.getElementById('paytriframe').src = `https://www.paytr.com/odeme/guvenli/${res_json.token}`;
            await loadJS("/payment_paytr_kt/static/src/lib/iframeResizer.min.js");
            window.iFrameResize({},'#paytriframe');
            $('#paytr_modal').modal('show')
        },

        /**
         * Prepare the inline form of Demo for direct payment.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} code - The code of the selected payment option's provider
         * @param {integer} paymentOptionId - The id of the selected payment option
         * @param {string} flow - The online payment flow of the selected payment option
         * @return {Promise}
         */
        _prepareInlineForm: function (code, paymentOptionId, flow) {

            if (code !== 'paytr') {
                return this._super(...arguments);
            }

            if (flow === 'token') {
                return Promise.resolve(); // Don't show the form for tokens
            }
            this._setPaymentFlow('direct');

            if (!document.getElementById('paytriframe')) {
                let html_src =  `<div id="paytr_modal" class="modal" tabindex="-1" role="dialog">` +
                '<div class="modal-dialog modal-lg" role="document">' +
                    '<div class="modal-content">' +
                        '<div class="modal-body">'+
                            '<iframe  id="paytriframe" frameborder="0" scrolling="no" style="width: 100%;"></iframe>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
                '</div>';
                document.querySelector('main').insertAdjacentHTML('beforeend', html_src)
            }

            return Promise.resolve()
        },

    };

    checkoutForm.include(paytrMixin);

});
