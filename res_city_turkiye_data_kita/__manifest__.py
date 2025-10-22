{
    "name": "Türkiye Semt - İlçe Bilgisi",
    "summary": """İş Ortağında city(İlçe) için seçilebilir alanda Türkiye semt/ilçe bilgisini ekler""",
    "description": """Bu modül, Odoo'daki İş Ortağı kayıtlarında bulunan city (İlçe) alanı için
            Türkiye'ye özgü semt/ilçe seçeneklerini ekler ve seçilebilir hale getirir. Amaç,
            adres doğruluğunu artırmak ve Türkiye'ye özel adres girdilerini standardize etmektir.""",
    "version": "17.0.1.0.3",
    "license": "LGPL-3",
    "author": "Kıta",
    "maintainer": "Kıta Yazılım",
    "support": "destek@kitayazilim.com",
    "website": "https://kitayazilim.com",
    "depends": ["base_address_extended", "contacts", "website"],
    "data": [
        "data/res.city.csv",
        "data/res_country_data.xml",
        "data/res_partner_data.xml",
    ],
    "images": [
        "static/description/main_screenshot.gif",
    ],
    "demo": [],
}
