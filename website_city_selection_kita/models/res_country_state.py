# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    def get_website_sale_cities(self, mode):
        return self.env['res.city'].search([('state_id', '=', self.id)])