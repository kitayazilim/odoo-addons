from werkzeug import urls
from collections import defaultdict
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.addons.payment import utils as payment_utils
from odoo.tools import groupby
from odoo.tools import SQL

import logging

_logger = logging.getLogger(__name__)


class PartnerAvgPaymentDays(models.Model):
    _name = "partner.avg.payment.days"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Partner Ortalama Ödeme Günleri"
    _rec_name = "partner_id"
    _order = "partner_id"

    partner_id = fields.Many2one(
        "res.partner",
        string="İş Ortağı",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sales_person_id = fields.Many2one(
        "res.users",
        string="Satış Temsilcisi",
        related="partner_id.user_id",
        store=True,
    )
    phone = fields.Char(
        string="Telefon",
        related="partner_id.phone",
        store=True,
    )
    mobile = fields.Char(
        string="Mobil",
        related="partner_id.mobile",
        store=True,
    )
    email = fields.Char(
        string="E-posta",
        related="partner_id.email",
        store=True,
    )
    category_id = fields.Many2many(
        "res.partner.category",
        string="Etiketler",
        compute="_compute_category_id",
        store=True,
    )
    note = fields.Text(string="Not")
    company_id = fields.Many2one(
        "res.company",
        string="Şirket",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Şirket Para Birimi",
        store=True,
    )
    avg_days = fields.Float(
        string="Ortalama Vade",
        digits=(16, 2),
        readonly=True,
    )
    credit_avg_days = fields.Float(
        string="Alacak Ort. Vade",
        digits=(16, 2),
        readonly=True,
        help="Alacak hesapları(credit) üzerinden hesaplanan ortalama vade günü",
    )
    debit_avg_days = fields.Float(
        string="Borç Ort. Vade",
        digits=(16, 2),
        readonly=True,
        help="Borç hesapları(debit) üzerinden hesaplanan ortalama vade günü",
    )
    last_activity_date = fields.Date(
        string="Son Hareket",
        help="İş ortağının alacak verecek hesaplarının son muhasebe hareket tarihi",
        readonly=True,
    )
    sync_date = fields.Datetime(
        string="Son Hesaplama",
        readonly=True,
        help="Ortalama ödeme günlerinin son hesaplandığı tarih",
    )
    payment_link_url = fields.Char(
        string="Ödeme Linki URL",
        compute="_compute_payment_link_url",
        help="SMS ve e-posta şablonlarında kullanılacak ödeme linki URL",
    )
    balance = fields.Monetary(
        string="Bakiye", currency_field="company_currency_id", readonly=True
    )
    readable_balance = fields.Char(compute="compute_readable_balance")
    balance_curr = fields.Monetary(
        string="Bakiye (Dövizli)",
        currency_field="company_currency_id",
        readonly=True,
        help="Güncel Kur ile dövizlilerin şirket para birimi karşılığı ve şirket para birimindeki bakiyeler toplamı. Özetle; Yabancı para birimi ile güncel kurdan çevrimi yapılmış bakiyeler + şirket para birimi cinsinden bakiyeler toplamı.",
    )
    balance_usd = fields.Float(
        string="Bakiye USD",
        currency_field="company_currency_id",
        readonly=True,
        digits=(16, 2),
    )
    balance_eur = fields.Float(
        string="Bakiye EUR",
        currency_field="company_currency_id",
        readonly=True,
        digits=(16, 2),
    )
    balance_curr_overdue = fields.Monetary(
        string="Geçmiş Bakiye (Dövizli)",
        currency_field="company_currency_id",
        readonly=True,
    )

    open_invoice_balance = fields.Monetary(
        string="Açık Sipariş",
        currency_field="company_currency_id",
        readonly=True,
        help="Henüz faturalandırılmamış açık siparişlerin toplam bakiyesi",
    )
    open_invoice_balance_usd = fields.Float(
        string="Açık Sipariş USD",
        readonly=True,
        digits=(16, 2),
    )
    open_invoice_balance_eur = fields.Float(
        string="Açık Sipariş EUR",
        readonly=True,
        digits=(16, 2),
    )

    last_sms_date = fields.Date(
        string="Son SMS Gönderimi",
        help="Son SMS gönderim tarihi",
        readonly=True,
    )
    last_email_date = fields.Date(
        string="Son E-posta Gönderimi",
        help="Son e-posta gönderim tarihi",
        readonly=True,
    )

    _sql_constraints = [
        (
            "partner_company_uniq",
            "unique(partner_id, company_id)",
            "Bu iş ortağı ve şirket için zaten bir kayıt var!",
        )
    ]

    def compute_readable_balance(self):
        for record in self:
            record.readable_balance = f"""{self.env.company.currency_id.with_context(lang=self.env.company.partner_id.lang).amount_to_text(record.balance)}"""

    @api.depends("partner_id", "partner_id.category_id")
    def _compute_category_id(self):
        for record in self:
            record.category_id = record.partner_id.category_id

    def _get_access_token(self):
        self.ensure_one()
        return payment_utils.generate_access_token(
            self.partner_id.id, self.balance, self.company_currency_id.id
        )

    def get_force_provider_id(self):
        ICP = self.env["ir.config_parameter"].sudo()
        force_provider = ICP.get_param(
            "payment_force_provider_id", "1"
        )  # Replace "some_parameter_key" with the actual key you need
        provider = self.env["payment.provider"]
        if force_provider and force_provider == "1":
            provider = (
                self.env.ref("payment_paytr_kt.payment_provider_paytr", False)
                or provider
            )
        return provider.id

    @api.depends("partner_id", "balance")
    def _compute_payment_link_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            if record.balance <= 0:
                record.payment_link_url = ""
                continue

            description = fields.datetime.now().strftime("%d%m%Y%H%M%S")
            amount = record.balance
            currency_id = record.company_currency_id.id
            partner_id = record.partner_id.id
            company_id = record.company_id.id

            params = {
                "reference": description,
                "access_token": self._get_access_token(),
                "amount": amount,
                "currency_id": currency_id,
                "force_provider_id": self.get_force_provider_id(),
                "company_id": company_id,
                "partner_id": partner_id,
            }
            filtered_dict = {
                k: v for k, v in params.items() if not v in (None, 0, "", False)
            }
            payment_link_url = (
                f"{base_url}/payment/pay?{urls.url_encode(filtered_dict)}"
            )
            record.payment_link_url = payment_link_url

    @api.depends_context("company")
    def _get_last_sync_date(self):
        """
        Son senkronizasyon tarihini sistem parametrelerinden alır.
        Eğer parametre yoksa, 365 gün öncesini döndürür.
        Şirket bazlı olarak çalışır.
        """
        company_id = self.env.company.id
        ICP = self.env["ir.config_parameter"].sudo()
        param_name = (
            f"partner_avg_payment_days_kita.last_sync_date.company_{company_id}"
        )
        last_sync_date_str = ICP.get_param(param_name)

        if last_sync_date_str:
            return fields.Datetime.from_string(last_sync_date_str)
        else:
            return fields.Datetime.now() - timedelta(days=365)

    @api.depends_context("company")
    def _set_last_sync_date(self, date):
        """
        Son senkronizasyon tarihini sistem parametrelerine kaydeder.
        Şirket bazlı olarak çalışır.
        """
        company_id = self.env.company.id
        ICP = self.env["ir.config_parameter"].sudo()
        param_name = (
            f"partner_avg_payment_days_kita.last_sync_date.company_{company_id}"
        )
        ICP.set_param(param_name, fields.Datetime.to_string(date))

    def get_partners_recent_activity_by_date(self, last_sync_date, company_id):
        self.env.cr.execute(
            """
            SELECT DISTINCT ON (partner_id) partner_id, account_move_line.write_date
            FROM account_move_line
            LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
            WHERE date >= %s AND partner_id IS NOT NULL AND account_move_line.company_id = %s AND a.account_type IN ('asset_receivable','liability_payable')
            ORDER BY partner_id, write_date DESC
        """,
            (last_sync_date, company_id),
        )

        return self.env.cr.fetchall()

    def get_partners_recent_activity_by_ids(self, partner_ids, company_id):
        self.env.cr.execute(
            """
            SELECT DISTINCT ON (partner_id) partner_id, account_move_line.write_date
            FROM account_move_line
            LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
            WHERE partner_id IN %s AND account_move_line.company_id = %s AND a.account_type IN ('asset_receivable','liability_payable')
            ORDER BY partner_id, write_date DESC
        """,
            (tuple(partner_ids), company_id),
        )

        return self.env.cr.fetchall()

    @api.model
    def _sync_partners(self):
        """
        Son senkronizasyon tarihinden sonra hareket olan partnerleri bulur ve
        partner.avg.payment.days modeline ekler.
        """

        last_sync_date = self._get_last_sync_date()
        company_id = self.env.company.id
        partners = self.get_partners_recent_activity_by_date(last_sync_date, company_id)
        max_date = False
        for row in partners:
            partner_id = row[0]
            write_date = row[1]
            if not max_date or write_date > max_date:
                max_date = write_date
            payment_days = self.search(
                [("partner_id", "=", partner_id), ("company_id", "=", company_id)]
            )
            if not payment_days:
                self.create(
                    {
                        "partner_id": partner_id,
                        "company_id": company_id,
                    }
                )

        if max_date:
            self._set_last_sync_date(max_date)

        return True

    def _sync_all_companies(self):
        companies = self.env["res.company"].search([])
        for company in companies:
            self.with_company(company)._sync_partners()

    @api.model
    def cron_calculate_avg_days(self, batch_size=False):
        """
        Henüz hesaplanmamış veya en eski hesaplama tarihine sahip partnerlerin
        ortalama ödeme günlerini hesaplar.
        Bu metod cron işi tarafından çağrılır.

        :param limit: Hesaplanacak maksimum partner sayısı
        """
        today = fields.Date.context_today(self)
        pay_avgs = self.search(
            ["|", ("sync_date", "=", False), ("sync_date", "<", today)]
        )
        if pay_avgs:
            BATCH_SIZE = batch_size or 100
            pay_avgs_batch = pay_avgs[:BATCH_SIZE]
            pay_avgs_batch._process_pay_avg()
            if len(pay_avgs) > BATCH_SIZE:
                self.env.ref(
                    "partner_avg_payment_days_kita.ir_cron_calculate_avg_days"
                )._trigger()
                return True

        return False

    def action_calculate_avg_days(self):
        self.last_activity_date = False
        self._process_pay_avg()

    def _process_pay_avg(self):
        """
        Henüz hesaplanmamış veya en eski hesaplama tarihine sahip partnerlerin
        ortalama ödeme günlerini hesaplar.
        Bu metod cron işi tarafından çağrılır.
        """

        self.env.cr.execute(
            """
            SELECT id FROM partner_avg_payment_days
            WHERE ID in %s
            FOR NO KEY UPDATE SKIP LOCKED
        """,
            [tuple(self.ids)],
        )

        record_ids = [r[0] for r in self.env.cr.fetchall()]
        records = self.browse(record_ids)
        if not records:
            return False

        for company, recs in groupby(records, lambda r: r.company_id):
            partner_ids = [rec.partner_id.id for rec in recs]
            partners_activity = self.get_partners_recent_activity_by_ids(
                partner_ids, company.id
            )
            partners_activity_dict = {r[0]: r[1] for r in partners_activity}

            all_records = self.env["partner.avg.payment.days"].concat(*recs)
            for rec in recs:
                activity_date = partners_activity_dict.get(rec.partner_id.id)
                if activity_date:
                    rec.last_activity_date = activity_date

            all_records.with_company(company)._calculate_avg_days()
            all_records.with_company(company)._credit_debit_curr()
            all_records.with_company(company)._get_open_invoice()

        _logger.info(
            "Partner ortalama ödeme günleri hesaplaması tamamlandı: %s partner işlendi",
            len(records),
        )
        return True

    @api.depends_context("company")
    def _get_open_invoice(self):
        """
        Vadesi geçmemiş alacakları hesaplar ve partner_id'ye göre gruplandırılmış bakiyeleri döndürür.
        """

        self.open_invoice_balance = False
        self.open_invoice_balance_usd = False
        self.open_invoice_balance_eur = False

        # SQL sorgusu ile hesaplama
        query = """
            SELECT
                sol.order_partner_id,
                so.currency_id,
                so.company_id,
                SUM(
                    (sol.product_uom_qty - sol.qty_invoiced)
                    * (sol.price_total / NULLIF(sol.product_uom_qty, 0))
                ) as uninvoiced_amount
            FROM sale_order_line sol
            INNER JOIN sale_order so ON sol.order_id = so.id
            WHERE sol.product_uom_qty > 0
            AND so.state = 'sale'
            AND so.company_id = %s
            AND sol.order_partner_id IN %s
            GROUP BY sol.order_partner_id, so.currency_id, so.company_id
            HAVING SUM(
                (sol.product_uom_qty - sol.qty_invoiced)
                * (sol.price_total / NULLIF(sol.product_uom_qty, 0))
            ) > 0
            ORDER BY sol.order_partner_id, so.currency_id
        """

        self.env.cr.execute(query, (self.company_id.id, tuple(self.partner_id.ids)))
        results = self.env.cr.dictfetchall()

        usd_currency = self.env.ref("base.USD")
        eur_currency = self.env.ref("base.EUR")

        # Sonuçları işle
        for item in results:
            record = self.filtered(
                lambda x: x.partner_id.id == item["order_partner_id"]
                and x.company_id.id == item["company_id"]
            )

            if item["currency_id"] != self.company_id.currency_id.id:
                currency = self.env["res.currency"].browse(item["currency_id"])
                record.open_invoice_balance += currency._convert(
                    item["uninvoiced_amount"],
                    self.company_id.currency_id,
                    self.company_id,
                    fields.Date.today(),
                )
            else:
                record.open_invoice_balance += item["uninvoiced_amount"]

            if item["currency_id"] == usd_currency.id:
                record.open_invoice_balance_usd += item["uninvoiced_amount"]
            elif item["currency_id"] == eur_currency.id:
                record.open_invoice_balance_eur += item["uninvoiced_amount"]

    def _calculate_avg_days(self):
        if not self.ids:
            return

        date_from_days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("partner_avg_payment_days_kita.date_from_days", 365)
        )

        today = fields.Date.context_today(self)
        date_from = today - timedelta(days=date_from_days)

        excluded_journal_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("partner_avg_payment_days_kita.excluded_journal_id", "")
        )

        domain = [
            ("partner_id", "in", self.partner_id.ids),
            ("parent_state", "=", "posted"),
            ("date", ">=", date_from),
            ("company_id", "=", self.env.company.id),
            (
                "account_id.account_type",
                "in",
                ("asset_receivable", "liability_payable"),
            ),
        ]

        if excluded_journal_id:
            domain.append(("journal_id", "!=", excluded_journal_id))

        move_lines = self.env["account.move.line"].search(domain, order="date desc")
        all_move_lines = move_lines.read(
            [
                "partner_id",
                "account_type",
                "date",
                "date_maturity",
                "credit",
                "debit",
                "move_name",
                "ref",
            ]
        )

        for record in self.with_company(
            self.env["res.company"].browse(self.env.company.id)
        ):
            record.balance = record.partner_id.credit - record.partner_id.debit
            record.note = f"Partner: {record.partner_id.name}\n"
            record.note += f"Bakiye: {record.balance:>.2f}\n"
            record.note += f"Borç Hesapları(debit): {record.partner_id.debit:>.2f}\n"
            record.note += (
                f"Alacak Hesapları(credit): {record.partner_id.credit:>.2f}\n\n"
            )
            record.write({"sync_date": fields.Datetime.now()})

            partner_lines = list(
                filter(
                    lambda x: x["partner_id"][0] == record.partner_id.id, all_move_lines
                )
            )
            calculation_types = [
                {
                    "field": "avg_days",
                    "balance": abs(record.balance),
                    "line_field": "debit" if record.balance > 0 else "credit",
                },
                {
                    "field": "debit_avg_days",
                    "balance": abs(record.partner_id.debit),
                    "line_field": "credit",
                },
                {
                    "field": "credit_avg_days",
                    "balance": abs(record.partner_id.credit),
                    "line_field": "debit",
                },
            ]

            for calc in calculation_types:
                record.note += "\n"
                record.note += f"--- {calc['field']} ---\n"

                if not partner_lines:
                    setattr(record, calc["field"], 0.0)
                    record.note += "Hareket bulunamadı\n\n"
                    continue

                total_amount = 0.0
                weighted_days = 0.0
                remaining_balance = calc["balance"]

                for line in partner_lines:
                    if (
                        calc["field"] == "credit_avg_days"
                        and line["account_type"] != "asset_receivable"
                    ):
                        continue

                    if (
                        calc["field"] == "debit_avg_days"
                        and line["account_type"] != "liability_payable"
                    ):
                        continue

                    if line[calc["line_field"]] <= 0:
                        continue

                    amount_to_consider = min(
                        line[calc["line_field"]], remaining_balance
                    )
                    if amount_to_consider <= 0:
                        continue

                    invoice_name = f"{line.get('move_name', '') or ''} {line.get('ref', '') or ''}".strip()
                    invoice_date = line["date"]
                    days = (today - invoice_date).days
                    weighted_days += days * amount_to_consider
                    total_amount += amount_to_consider
                    remaining_balance -= amount_to_consider

                    record.note += f"{invoice_date} | {amount_to_consider:>10.2f} | {invoice_name}\n"

                    if remaining_balance <= 0:
                        break

                if remaining_balance > 0:
                    amount_to_consider = remaining_balance
                    invoice_date = date_from
                    days = (today - invoice_date).days
                    weighted_days += days * amount_to_consider
                    total_amount += amount_to_consider
                    record.note += (
                        f"{invoice_date} | {amount_to_consider:>10.2f} | Kalan bakiye\n"
                    )

                if total_amount > 0:
                    setattr(record, calc["field"], weighted_days / total_amount)
                else:
                    setattr(record, calc["field"], 0.0)

    def action_send_sms(self):
        """SMS'i gönder"""
        template = self.env.ref(
            "partner_avg_payment_days_kita.sms_template_balance_notify"
        )
        today = fields.Date.context_today(self)
        force_sent = self.env.context.get("force_sent", False)

        for rec in self:
            sms_interval_days = rec.company_id.sms_interval_days

            if (
                not force_sent
                and rec.last_sms_date
                and sms_interval_days
                and (today - rec.last_sms_date).days < sms_interval_days
            ):
                continue

            composer = self.env["sms.composer"].create(
                {
                    "template_id": template.id,
                    "res_model": self._name,
                    "res_id": rec.id,
                    "composition_mode": "comment",
                    "recipient_single_number_itf": rec.partner_id.mobile,
                }
            )
            composer._action_send_sms()
            rec.write({"last_sms_date": today})

    def action_email_data(self):
        today = fields.Date.context_today(self)

        template = self.env.ref(
            "partner_avg_payment_days_kita.mail_template_balance_notify"
        )
        force_sent = self.env.context.get("force_sent", False)
        for record in self:
            email_interval_days = record.company_id.email_interval_days

            if (
                not force_sent
                and record.last_email_date
                and email_interval_days
                and (today - record.last_email_date).days < email_interval_days
            ):
                continue

            template.send_mail(record.id, force_send=True)
            record.write({"last_email_date": today})

    def _get_default_payment_link_values(self):
        self.ensure_one()
        return {
            "description": "odeme_tahsilat_linki",
            "currency_id": self.env.company.currency_id.id,
            "partner_id": self.partner_id.id,
            "amount": self.balance,
            "amount_max": self.balance,
        }

    def action_create_payment_link(self):
        self.ensure_one()
        res_id = self.env["payment.link.wizard"].create(
            {
                "res_id": self.id,
                "res_model": self._name,
                "currency_id": self.env.company.currency_id.id,
                "partner_id": self.partner_id.id,
                # "description": description,
                "amount": self.balance,
                "amount_max": self.balance,
            }
        )

        title = "Bakiyeye Ödeme Linki Oluşturma"
        return {
            "name": title,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "payment.link.wizard",
            "res_id": res_id.id,
            "context": {"force_provider_id": self.get_force_provider_id()},
            "target": "new",
        }

    @api.depends_context("company")
    def _credit_debit_curr(self):
        if not self.ids:
            self.balance_curr = False
            self.balance_curr_overdue = False
            self.balance_usd = False
            self.balance_eur = False
            return

        company_currency_id = self.env.company.currency_id
        currency_usd_id = self.env.ref("base.USD").id
        currency_eur_id = self.env.ref("base.EUR").id
        self.balance_curr = False
        self.balance_usd = False
        self.balance_eur = False
        self.balance_curr_overdue = False

        query = self.env["account.move.line"]._where_calc(
            [
                ("parent_state", "=", "posted"),
                ("company_id", "child_of", self.env.company.root_id.id),
            ]
        )
        self.env["account.move.line"].flush_model(
            [
                "account_id",
                "amount_residual_currency",
                "company_id",
                "parent_state",
                "partner_id",
                "reconciled",
            ]
        )
        self.env["account.account"].flush_model(["account_type"])
        sql = SQL(
            """
            SELECT account_move_line.partner_id, account_move_line.currency_id, SUM(account_move_line.amount_residual_currency)
            FROM %s
            LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
            WHERE a.account_type IN ('asset_receivable','liability_payable')
            AND account_move_line.partner_id IN %s
            AND account_move_line.reconciled IS NOT TRUE
            AND %s
            GROUP BY account_move_line.partner_id, account_move_line.currency_id
            """,
            query.from_clause,
            tuple(self.partner_id.ids),
            query.where_clause or SQL("TRUE"),
        )

        for pid, currency_id, val in self.env.execute_query(sql):
            record = self.filtered(
                lambda x: x.partner_id.id == pid
                and x.company_id.id == self.env.company.id
            )
            if currency_id == currency_usd_id:
                record.balance_usd += val
            elif currency_id == currency_eur_id:
                record.balance_eur += val

            if currency_id != company_currency_id.id:
                currency = self.env["res.currency"].browse(currency_id)
                val = currency._convert(
                    val, company_currency_id, self.env.company, fields.Date.today()
                )
            record.balance_curr += val

        # future_receivables
        today = fields.Date.today()
        query = self.env["account.move.line"]._where_calc(
            [
                ("parent_state", "=", "posted"),
                ("date_maturity", ">", today),
                ("company_id", "child_of", self.env.company.root_id.id),
            ]
        )

        sql = SQL(
            """
            SELECT account_move_line.partner_id, account_move_line.currency_id, SUM(account_move_line.amount_residual_currency)
            FROM %s
            LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
            WHERE a.account_type = 'asset_receivable'
            AND account_move_line.partner_id IN %s
            AND account_move_line.reconciled IS NOT TRUE
            AND %s
            GROUP BY account_move_line.partner_id, account_move_line.currency_id
            """,
            query.from_clause,
            tuple(self.partner_id.ids),
            query.where_clause or SQL("TRUE"),
        )

        future_receivables = defaultdict(float)
        for pid, currency_id, val in self.env.execute_query(sql):
            record = self.filtered(
                lambda x: x.partner_id.id == pid
                and x.company_id.id == self.env.company.id
            )
            if currency_id != company_currency_id.id:
                val = currency_id._convert(
                    val,
                    company_currency_id,
                    self.env.company,
                    today,
                )
            future_receivables[record] += val

        for k, v in future_receivables.items():
            k.balance_curr_overdue = k.balance_curr - v
