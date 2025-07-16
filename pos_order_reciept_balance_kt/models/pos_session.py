# Copyright 2023 Kita Yazilim
# License LGPLv3 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models



class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_partner(self):
        result = super()._loader_params_res_partner()
        result['search_params']['fields'].append('credit')
        result['search_params']['fields'].append('debit')
        return result
    
    # TODO
    # def get_pos_ui_res_partner_by_params(self):
    #     # bu fonksiyon ile çekilen data tarihini bakiye tarihi olarak ver!!
    
 