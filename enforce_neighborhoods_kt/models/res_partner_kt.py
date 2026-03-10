from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResPartnerKt(models.Model):
    _inherit = 'res.partner'

    neighborhood_kt_id = fields.Many2one('res.neighborhood.kt', string='Neighborhood', domain="[('city_id', '=', city_id)]")
    neighborhood_kt_name = fields.Char(string='Neighborhood Name', related='neighborhood_kt_id.name', readonly=True)
    country_enforce_neighborhoods_kt = fields.Boolean(related='country_id.enforce_neighborhoods_kt',
                                                 string='Country Enforces Neighborhoods', readonly=True)

    @api.onchange('city_id')
    def _onchange_city_id(self):
        res = super(ResPartnerKt, self)._onchange_city_id()
        if self.city_id and self.neighborhood_kt_id and self.neighborhood_kt_id.city_id != self.city_id:
            self.neighborhood_kt_id = False
        return res

    @api.constrains('country_id', 'state_id', 'neighborhood_kt_id')
    def _check_neighborhood_kt_required(self):
        # users = self.env['res.users'].sudo().search([('partner_id', 'in', self.ids)])
        # users_partner_ids = users.mapped('partner_id')
        # and partner.id not in users_partner_ids:
        for partner in self:
            if partner.country_id and partner.state_id and partner.country_id.enforce_neighborhoods_kt and not partner.neighborhood_kt_id:
                raise ValidationError(_("Neighborhood is required for addresses in %s.") % partner.country_id.name)

    @api.constrains('country_id', 'state_id', 'city_id', 'neighborhood_kt_id')
    def _check_neighborhood_kt_hierarchy(self):
        for partner in self:
            if partner.neighborhood_kt_id:
                if partner.neighborhood_kt_id.city_id != partner.city_id:
                    raise ValidationError(_("The neighborhood must belong to the selected city."))

    @api.model
    def _address_fields(self):
        return super(ResPartnerKt, self)._address_fields() + ['neighborhood_kt_name']