from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteNeighborhoodKt(WebsiteSale):

    WRITABLE_PARTNER_FIELDS = WebsiteSale.WRITABLE_PARTNER_FIELDS + ['neighborhood_kt_id']

    def _get_country_related_render_values(self, kw, render_values):
        '''
        This method provides fields related to the country to render the website sale form
        '''
        values = render_values['checkout']
        mode = render_values['mode']
        order = render_values['website_sale_order']

        res = super(WebsiteNeighborhoodKt, self)._get_country_related_render_values(kw, render_values)
        city = 'city_id' in values and values['city_id'] != '' and res.get('country', {}).enforce_neighborhoods_kt and request.env['res.city'].browse(int(values['city_id']))
        city = city and city.exists() or request.env['res.city']

        res.update({
            'city_neighborhoods': city and city.neighborhood_kt_ids or []
        })
        return res

    @http.route()
    def country_infos(self, country, mode, **kw):
        """Override to add enforce_cities flag to the response."""
        result = super().country_infos(country, mode, **kw)
        result['neighborhood_required'] = country.enforce_neighborhoods_kt
        return result

    @http.route(['/shop/neighborhoods_kt'], type='json', auth="public", methods=['POST'], website=True)
    def neighborhoods_kt(self, city_id, **kw):
        if not city_id:
            return []

        neighborhoods = request.env['res.neighborhood.kt'].sudo().search([
            ('city_id', '=', int(city_id))
        ])
        return [(n.id, n.name) for n in neighborhoods]

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super(WebsiteNeighborhoodKt, self).checkout_form_validate(mode, all_form_values, data)

        # Check if country enforces neighborhoods
        if all_form_values.get('country_id'):
            country = request.env['res.country'].sudo().browse(int(all_form_values.get('country_id')))
            if country.exists() and country.enforce_neighborhoods_kt and not all_form_values.get('neighborhood_kt_id'):
                error['neighborhood_kt_id'] = 'error'
                error_message.append('Neighborhood is required for the selected country.')

        return error, error_message

    def values_preprocess(self, values):
        new_values = super().values_preprocess(values)
        neighborhood_kt_id = new_values.get('neighborhood_kt_id')
        if neighborhood_kt_id:
            country = request.env["res.country"].browse(new_values.get('country_id'))
            if country and country.enforce_cities:
                city = request.env["res.city"].browse(neighborhood_kt_id)
                if city.exists():
                    # Update city name from city_id
                    new_values['city'] = city.name

        return new_values

    def _get_mandatory_fields_billing(self, country_id=False):
        req = super()._get_mandatory_fields_billing(country_id)
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.enforce_neighborhoods_kt:
                req += ['neighborhood_kt_id']
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        req = super()._get_mandatory_fields_shipping(country_id)
        if country_id:
            country = request.env['res.country'].browse(country_id)
            if country.enforce_neighborhoods_kt:
                req += ['neighborhood_kt_id']
        return req
