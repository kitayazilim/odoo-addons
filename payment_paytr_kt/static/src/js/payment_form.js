/** @odoo-module **/

import { loadJS } from '@web/core/assets';
import { _t } from '@web/core/l10n/translation';
import { rpc, RPCError } from '@web/core/network/rpc';
import { patch } from '@web/core/utils/patch';
import { PaymentForm } from '@payment/interactions/payment_form';

patch(PaymentForm.prototype, {

    setup() {
        super.setup();
        this.paytrData = {}; // Store the form data of each instantiated payment method.
    },

    async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'paytr') {
            await super._prepareInlineForm(...arguments);
            return;
        } else if (flow === 'token') {
            return;
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
            return; // Don't re-extract the data if already done for this payment method.
        }
    },

    async _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== 'paytr') {
            await super._processDirectFlow(...arguments);
            return;
        }

        // Initiate the payment
        await rpc('/payment/paytr/get-iframe-token', {
            'reference': processingValues.reference,
            'providerId': processingValues.provider_id
        }).then( async (result) => {
            this._enableButton();
            // $('body').unblock();
            document.getElementById('paytriframe').src = `https://www.paytr.com/odeme/guvenli/${result.token}`;
            await loadJS("/payment_paytr_kt/static/src/lib/iframeResizer.min.js");
            $('#paytr_modal').modal('show');
            window.iFrameResize({},'#paytriframe');

        }).catch((error) => {
            if (error instanceof RPCError) {
                this._displayErrorDialog(_t("Payment processing failed"), error.data.message);
                this._enableButton();
            } else {
                return Promise.reject(error);
            }
        });
    },


})

