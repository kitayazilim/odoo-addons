from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    partner_avg_payment_days_from = fields.Integer(
        string='Ortalama Ödeme Günleri Hesaplama Süresi (gün)',
        config_parameter='partner_avg_payment_days_kita.date_from_days',
        default=365,
        help='Ortalama ödeme günleri hesaplaması için geriye dönük gün sayısı'
    )

    partner_avg_payment_excluded_journal_id = fields.Many2one(
        'account.journal',
        string='Hariç Tutulacak Yevmiye',
        config_parameter='partner_avg_payment_days_kita.excluded_journal_id',
        help='Ortalama ödeme günleri hesaplamasından hariç tutulacak yevmiye'
    )

    partner_avg_payment_sms_interval_days = fields.Integer(
        string='SMS Gönderim Sıklığı (gün)',
        related='company_id.sms_interval_days',
        readonly=False,
        help='Aynı iş ortağına yeniden SMS göndermek için beklenecek minimum gün sayısı'
    )

    partner_avg_payment_email_interval_days = fields.Integer(
        string='E-posta Gönderim Sıklığı (gün)',
        related='company_id.email_interval_days',
        readonly=False,
        help='Aynı iş ortağına yeniden e-posta göndermek için beklenecek minimum gün sayısı'
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
