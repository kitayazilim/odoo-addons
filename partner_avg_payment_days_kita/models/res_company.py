from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    sms_interval_days = fields.Integer(
        string='SMS Gönderim Sıklığı (gün)',
        default=7,
        help='Aynı iş ortağına yeniden SMS göndermek için beklenecek minimum gün sayısı'
    )

    email_interval_days = fields.Integer(
        string='E-posta Gönderim Sıklığı (gün)',
        default=7,
        help='Aynı iş ortağına yeniden e-posta göndermek için beklenecek minimum gün sayısı'
    )