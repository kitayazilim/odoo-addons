# Copyright 2024 Kita Yazilim
# License LGPLv3 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api , models


class PosPayment(models.Model):

    _inherit = "pos.payment"

    @api.model
    def get_partner_balance(self, partner_id):
        partner_id = self.env['res.partner'].browse(partner_id)
        balance = partner_id.credit - partner_id.debit
        payment_methods = self.env['pos.payment.method'].search([]).filtered(lambda m: m.journal_id.type not in ['cash', 'bank'])
        domain = [
            ('pos_order_id.partner_id', '=', partner_id.id), 
            ('pos_order_id.state', '=', 'paid'), 
            ('payment_method_id', 'in', payment_methods.ids)]
        
        result = self.env['pos.payment']._read_group(domain, ['amount'], ['session_id'])
        return balance + (result and result[0]['amount'] or 0.0) 

