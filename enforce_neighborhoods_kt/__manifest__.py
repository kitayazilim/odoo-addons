{
    "name": "Semt - İlçe Bilgisi Zorunluluğu",
    "version": "1.0",
    "category": "Hidden/Tools",
    "description": """
Bu modül, Odoo'daki İş Ortağı kayıtlarında bulunan city (İlçe) alanı için Türkiye'ye özgü semt/ilçe seçeneklerini ekler ve seçilebilir hale getirir.
Amaç, adres doğruluğunu artırmak ve Türkiye'ye özel adres girdilerini standardize etmektir.
Ayrıca, bu modül ile semt/ilçe bilgisi zorunlu hale getirilerek, eksik veya hatalı adres girişlerinin önüne geçilir.
Böylece, müşteri veritabanının kalitesi yükseltilir ve lojistik süreçlerde yaşanabilecek sorunlar minimize edilir.
    """,
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
    "license": "LGPL-3",
    "author": "Kıta Yazılım",
    "installable": True,
    "application": False,
}
