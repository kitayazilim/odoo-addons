# -*- coding: utf-8 -*-
{
    "name": "Website City Selection",
    "version": "1.0",
    "category": "Website/Website",
    "summary": "Add city dropdown selection to website address form",
    "description": """
Website City Selection
=====================
This module adds a city dropdown selection to the website address form when the country has the enforce_cities feature enabled.
It provides a consistent user experience between the backend and website interfaces for address entry.
    """,
    "author": "Kıta",
    "website": "https://kitayazilim.com",
    "support": "support@kitayazilim.com",
    "depends": ["website_sale", "base_address_extended"],
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_city_selection_kita/static/src/js/website_city_selection.js",
        ],
    },
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
