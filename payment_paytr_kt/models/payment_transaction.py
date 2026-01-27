# -*- coding: utf-8 -*-
# Part of Kitayazilim. See LICENSE file for full copyright and licensing details.

"""Payment Transaction Model Extensions for PayTR

This module extends the payment.transaction model to add PayTR-specific
functionality for handling payment transactions through the PayTR
payment gateway.
"""

import logging
import re
from odoo import _, api, models
from odoo.addons.payment import utils as payment_utils
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    """Payment Transaction Model Extension for PayTR

    This class extends the payment.transaction model to add PayTR-specific
    methods for handling transaction references and processing payment
    notifications from the PayTR payment gateway.
    """
    _inherit = 'payment.transaction'

    @api.model
    def _compute_reference(self, provider_code, prefix=None, separator='-', **kwargs):
        """Compute a unique reference for the transaction.

        For PayTR, we need to ensure that the reference contains only alphanumeric
        characters without any special characters or spaces, as required by the
        PayTR API specifications.

        Args:
            provider_code: The code of the payment provider
            prefix: Optional prefix for the reference
            separator: The separator to use between prefix and reference

        Returns:
            str: A unique transaction reference
        """
        if provider_code != 'paytr':
            return super()._compute_reference(provider_code, prefix=prefix, **kwargs)

        prefix = payment_utils.singularize_reference_prefix(prefix="", separator="")
        return super()._compute_reference(provider_code, prefix=re.sub(r'[\W]', '', prefix or ''), separator="", **kwargs)

    @api.model
    def _extract_reference(self, provider_code, payment_data):
        """Override of `payment` to extract the reference from the APS data."""
        if provider_code != 'paytr':
            return super()._extract_reference(provider_code, payment_data)
        return payment_data.get('merchant_oid')

    def _extract_amount_data(self, payment_data):
        """Override of `payment` to extract the amount and currency from the payment data."""
        if self.provider_code != 'paytr':
            return super()._extract_amount_data(payment_data)

        currency = payment_data.get('currency')
        if currency == 'TL':
            currency = 'TRY'

        return {
            'amount': payment_data.get('amount'),
            'currency_code': currency,
        }

    def _apply_updates(self, notification_data):
        """Process the transaction based on PayTR notification data.

        This method updates the transaction status based on the notification
        data received from PayTR. It handles success and failure cases.

        Args:
            notification_data: The normalized notification data from PayTR

        Raises:
            ValidationError: If inconsistent data were received
        """
        """ Override of payment to process the transaction based on Buckaroo data.

        Note: self.ensure_one()

        :param dict notification_data: The normalized notification data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._apply_updates(notification_data)
        if self.provider_code != 'paytr':
            return

        transaction_status = notification_data.get('status')
        if not transaction_status:
            raise ValidationError("PayTR: " + _("Received data with missing transaction status"))

        code = notification_data.get('failed_reason_code', '')
        msg = notification_data.get('failed_reason_msg', '')

        if transaction_status == "success":
            self._set_done()
        elif transaction_status == "failed":
            self._set_error(_(
                "An error occurred during processing of your payment. Please try again."
                "(%s) %s",
                code, msg
            ))
        else:
            _logger.warning(
                "received data with invalid payment status (%s) for transaction with reference %s",
                transaction_status, self.reference
            )
            self._set_error("PayTR: " + _("Unknown status! Message: %s", msg))
