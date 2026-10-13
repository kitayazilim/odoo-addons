# Part of Odoo. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.payment.tests.http_common import PaymentHttpCommon
from odoo.addons.payment_paytr_kt.controllers.main import PayTRController
from odoo.addons.payment_paytr_kt.tests.common import PayTRCommon


@tagged("post_install", "-at_install")
class TestProcessingFlows(PayTRCommon, PaymentHttpCommon):
    @mute_logger("odoo.addons.payment_paytr_kt.controllers.main")
    def test_webhook_notification_triggers_processing(self):
        """Test that receiving a valid webhook notification triggers the processing of the
        payment data."""
        self._create_transaction("direct")
        url = self._build_url(PayTRController._return_url)

        with patch("odoo.addons.payment.models.payment_transaction.PaymentTransaction._record") as record_mock:
            self._make_http_post_request(url, data=self.webhook_paytr_data)

        self.assertEqual(record_mock.call_count, 1)
