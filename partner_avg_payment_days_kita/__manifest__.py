{
    "name": "Partner Ortalama Vade Günleri",
    "version": "18.0.1.0.3",
    "category": "Accounting",
    "summary": "İş ortaklarının ortalama vade günlerini hesaplar",
    "description": """
        Bu modül, iş ortaklarının ortalama vade günlerini (vade) hesaplar ve saklar.
        Özellikler:
        - İş ortaklarının ortalama vade günlerini hesaplama
        - Arka planda çalışan cron işleri ile otomatik hesaplama
    """,
    "author": "Kıta",
    "website": "https://kitayazilim.com",
    "depends": ["account", "payment", "sale", "sms", "payment_paytr_kt"],
    "data": [
        "security/ir.model.access.csv",
        "data/cron_data.xml",
        "data/server_action.xml",
        "data/message_template_data.xml",
        "views/partner_payment_days_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu_views.xml",
    ],
    "images": ["static/description/partner_avg_payment_days_banner.png"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
