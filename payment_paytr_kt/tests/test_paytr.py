# Part of Odoo. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_paytr_kt.tests.common import PayTRCommon


@tagged("post_install", "-at_install")
class PayTRTest(PayTRCommon):
    def test_available_providers(self):
        # Note: in the test common, 'USD' is specified as the currency linked to the user account.
        unsupported_currency = self._enable_currency("CHF")
        providers = self.env["payment.provider"]._find_available_providers(
            self.company.id, self.partner.id, self.amount, currency_id=unsupported_currency.id
        )
        self.assertNotIn(self.paytr, providers)
        providers = self.env["payment.provider"]._find_available_providers(
            self.company.id, self.partner.id, self.amount, currency_id=self.currency_tr.id
        )
        self.assertIn(self.paytr, providers)
