from odoo import api, fields, models

class ResNeighborhoodKt(models.Model):
    _name = 'res.neighborhood.kt'
    _description = 'Neighborhood'
    _order = 'name'

    name = fields.Char(string='Neighborhood Name', required=True, translate=True)
    code = fields.Char(string='Neighborhood Code')
    city_id = fields.Many2one('res.city', string='City', required=True, ondelete='cascade')
    state_id = fields.Many2one('res.country.state', related='city_id.state_id', store=True, readonly=True)
    country_id = fields.Many2one('res.country', related='city_id.country_id', store=True, readonly=True)

    _sql_constraints = [
        ('name_city_uniq', 'unique(name, city_id)', 'The neighborhood name must be unique per city!')
    ]

    # def name_get(self):
    #     result = []
    #     for record in self:
    #         result.append((record.id, "{} ({} / {})".format(record.name, record.city_id.name, record.state_id.name)))
    #     return result