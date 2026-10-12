from odoo import models


class PaymentLinkWizard(models.TransientModel):
    _inherit = 'payment.link.wizard'

    def _prepare_query_params(self, related_document):
        """Override to optionally use company currency based on partner flag.

        If partner has use_company_currency enabled, use self.company_id.currency_id
        instead of the document currency, and generate the access token with the
        same currency to keep validation consistent.
        """
        res = super()._prepare_query_params(related_document)
        force_provider_id = self.env.context.get("force_provider_id")
        if force_provider_id:
            res.update({
                'force_provider_id': force_provider_id,
            })

        return res