# -*- coding: utf-8 -*-
# Part of Kitayazilim. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """Filter providers based on currency compatibility.

        Args:
            currency_id: The ID of the currency to check compatibility with

        Returns:
            recordset: Compatible payment providers
        """
        """ Override of `payment` to unlist Bank of Georgia providers for unsupported currencies. """
        providers = super()._get_compatible_providers(
            *args, currency_id=currency_id, **kwargs
        )
        force_provider_id = kwargs.get("force_provider_id", False)

        if force_provider_id:
            providers = providers.filtered(lambda p: p.id == int(force_provider_id))

        return providers
