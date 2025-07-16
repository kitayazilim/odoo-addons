# Copyright 2025 Kıta Yazılım
# License LGPLv3 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "POS Receipt Category and UoM Quantities",
    "summary": """Adds Category and UoM Quantities to POS Receipt""",
    "version": "1.0.0",
    "license": "LGPL-3",
    "author": "Kıta",
    "website": "kitayazilim.com",
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_receipt_category_totals_kt/static/src/js/OrderReceipt.js",
            "pos_receipt_category_totals_kt/static/src/xml/order_receipt.xml",
        ],
    },
    "data": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}
