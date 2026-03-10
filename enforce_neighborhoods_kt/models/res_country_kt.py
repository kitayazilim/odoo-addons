from odoo import api, fields, models

class ResCountryKt(models.Model):
    _inherit = 'res.country'

    enforce_neighborhoods_kt = fields.Boolean(string='Enforce Neighborhoods', default=False,
                                             help="If checked, neighborhood will be a required field for addresses in this country")
