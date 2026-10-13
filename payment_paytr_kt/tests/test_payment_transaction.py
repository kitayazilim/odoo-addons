# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged

from odoo.addons.payment_paytr_kt.tests.common import PayTRCommon


@tagged("post_install", "-at_install")
class TestPaymentTransaction(PayTRCommon):
    def test_search_by_reference_finds_transaction_from_webhook_data(self):
        """Test that a transaction is correctly found from webhook data using merchant_oid."""
        tx = self._create_transaction("direct")
        found_tx = self.env["payment.transaction"]._search_by_reference(
            "paytr", self.webhook_paytr_data
        )
        self.assertEqual(tx, found_tx)

    def test_reference_contains_only_valid_characters(self):
        """Test that transaction references are made of only alphanumerics."""
        for prefix in (None, "", "S0001", "INV/20222/001", "dummy ref", "xc_rf"):
            reference = self.env["payment.transaction"]._compute_reference("paytr", prefix=prefix)
            self.assertRegex(reference, r"^[a-zA-Z0-9]*$")

    def test_processing_payment_data_confirms_transaction(self):
        """Test that the transaction state is set to 'done' when the payment data indicate a
        successful payment."""
        tx = self._create_transaction(flow="redirect")
        tx.with_context(payment_safe_write=True)._apply_updates(self.webhook_paytr_data)
        self.assertEqual(tx.state, "done")
