# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCity(WebsiteSale):
    """Extends the WebsiteSale controller to handle city selection."""

    # Add city_id to writable fields
    WRITABLE_PARTNER_FIELDS = WebsiteSale.WRITABLE_PARTNER_FIELDS + ["city_id"]

    @http.route(
        ['/shop/country_infos/<model("res.country"):country>'],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def country_infos(self, country, mode, **kw):
        """Override to add enforce_cities flag to the response."""
        result = super(WebsiteSaleCity, self).country_infos(country, mode, **kw)
        result["enforce_cities"] = country.enforce_cities
        return result

    @http.route(
        ['/shop/state_infos/<model("res.country.state"):state>'],
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
    )
    def state_infos(self, state, **kw):
        """Get cities for a given state."""
        cities = request.env["res.city"].search([("state_id", "=", state.id)])
        return {
            "cities": [(city.id, city.name) for city in cities],
        }

    def _include_country_and_state_in_address(self, address):
        """Override to handle city_id in address processing."""
        result = super(WebsiteSaleCity, self)._include_country_and_state_in_address(
            address
        )

        # Handle city_id if present
        city_id = address.get("city_id")
        if city_id and isinstance(city_id, str) and city_id.isdigit():
            city_id = int(city_id)
            country = address.get("country_id")
            if country and country.enforce_cities:
                city = request.env["res.city"].browse(city_id)
                if city.exists():
                    # Update city name from city_id
                    address["city"] = city.name

        return result

    def values_preprocess(self, values):
        new_values = super(WebsiteSaleCity, self).values_preprocess(values)
        city_id = new_values.get("city_id")
        if city_id:
            country = request.env["res.country"].browse(new_values.get("country_id"))
            if country and country.enforce_cities:
                city = request.env["res.city"].browse(city_id)
                if city.exists():
                    # Update city name from city_id
                    new_values["city"] = city.name

        return new_values

    def _get_mandatory_fields_billing(self, country_id=False):
        req = super(WebsiteSaleCity, self)._get_mandatory_fields_billing(country_id)
        if country_id:
            country = request.env["res.country"].browse(country_id)
            if country.enforce_cities:
                req += ["city_id"]
        return req

    def _get_mandatory_fields_shipping(self, country_id=False):
        req = super(WebsiteSaleCity, self)._get_mandatory_fields_shipping(country_id)
        if country_id:
            country = request.env["res.country"].browse(country_id)
            if country.enforce_cities:
                req += ["city_id"]
        return req

    def _get_country_related_render_values(self, kw, render_values):
        """
        This method provides fields related to the country to render the website sale form
        """
        values = render_values["checkout"]
        mode = render_values["mode"]

        res = super(WebsiteSaleCity, self)._get_country_related_render_values(
            kw, render_values
        )
        state = (
            "state_id" in values
            and values["state_id"] != ""
            and res.get("country", {}).enforce_cities
            and request.env["res.country.state"].browse(int(values["state_id"]))
        )
        state = state and state.exists() or request.env["res.country.state"]

        res.update(
            {
                "state": state,
                "state_cities": state.get_website_sale_cities(mode=mode[1]),
            }
        )
        return res
