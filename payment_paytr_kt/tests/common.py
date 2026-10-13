# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.fields import Command

from odoo.addons.payment.tests.common import PaymentCommon


class PayTRCommon(PaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency_tr = cls._enable_currency("TRY")

        cls.paytr = cls._prepare_provider(
            "paytr",
            update_values={
                "paytr_merchant_id": "123456",
                "paytr_merchant_key": "XXXYYYZZZ",
                "paytr_merchant_salt": "XXXYYYZZZ",
                "available_currency_ids": [Command.set(cls.currency_tr.ids)],
            },
        )

        cls.provider = cls.paytr
        cls.currency = cls.currency_tr
        cls.reference = "ABC123"

        cls.payment_paytr_data = {
            "merchant_id": "123456",
            "user_ip": "1.1.1.1",
            "merchant_oid": "ABC123",
            "email": "user@domainname.com",
            "payment_amount": "100",
            "total_amount": "100",
            "status": "success",
            "user_basket": "W1siXHUwMGQ2cm5layBcdTAwZmNyXHUwMGZjbiAxIiwiMTguMDAiLDFdLFsiXHUwMGQ2cm5layBcdTAwZmNyXHUwMGZjbiAyIiwiMzMuMjUiLDJdLFsiXHUwMGQ2cm5layBcdTAwZmNyXHUwMGZjbiAzIiwiNDUuNDIiLDFdXQ==",
            "no_installment": "0",
            "max_installment": "12",
            "currency": "TL",
            "test_mode": "0",
            "merchant_salt": "XXXYYYZZZ",
            "merchant_key": "XXXYYYZZZ"
        }

        # Base webhook notification structure
        cls.webhook_paytr_data = {
            "hash": "6dDSyMFnQ6eANVo43BWHrgsfCj6vVoI9hyf0XMCWGP4=",
            "merchant_oid": "ABC123",
            "status": "success",
            "total_amount": "100",
            "payment_type": "card",
            "payment_amount": "100",
            "currency": "TL"
        }
