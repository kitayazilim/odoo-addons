{
    "name": "Mahalle Bilgisi Zorunluluğu",
    "description": """
        Bu modül, Odoo'daki İş Ortağı kayıtlarında bulunan city (İlçe) alanı için mahalle bilgilerini getirir.
        data dosyasında bulunan res.partner.csv dosyasındaki kayıtlar, res.partner modeline eklenir ve city alanına bağlı olarak mahalle bilgisi sağlanır.
         - res.partner modeline mahalle bilgisi ekler
         - city alanına bağlı olarak mahalle bilgisi sağlar
    """,
    "category": "Sales/CRM",
    "version": "18.0.1.0.1",
    "license": "LGPL-3",
    "author": "Kıta",
    "maintainer": "Kıta Yazılım",
    "depends": ["base", "base_address_extended", "website", "website_sale", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "data/res_partner_data.xml",
        "views/res_country_kt_views.xml",
        "views/res_partner_kt_views.xml",
        "views/res_neighborhood_kt_views.xml",
        "views/res_city_kt_views.xml",
        "views/website_sale_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "enforce_neighborhoods_kt/static/src/js/address_form.js",
        ],
    },
    "images": [
        "static/description/cover.png",
    ],
    "installable": True,
    "application": False,
}
