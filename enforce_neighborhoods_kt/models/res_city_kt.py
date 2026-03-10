from odoo import api, fields, models

class ResCityKt(models.Model):
    _inherit = 'res.city'

    neighborhood_kt_ids = fields.One2many('res.neighborhood.kt', 'city_id', string='Neighborhoods')
    neighborhood_kt_count = fields.Integer(compute='_compute_neighborhood_kt_count', string='Number of Neighborhoods', store=True)

    @api.depends('neighborhood_kt_ids')
    def _compute_neighborhood_kt_count(self):
        for city in self:
            city.neighborhood_kt_count = len(city.neighborhood_kt_ids)
