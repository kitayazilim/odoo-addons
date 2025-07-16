# Copyright 2023 Kita Yazilim
# License LGPLv3 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "POS Order Receipt Balance",
    "summary": """Adds Balance to POS Receipt""",
    "version": "1.0.0",
    "license": "LGPL-3",
    "author": "Kıta",
    "website": "kitayazilim.com",
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale.assets": [
            "pos_order_reciept_balance_kt/static/src/js/OrderReceipt.js",
            "pos_order_reciept_balance_kt/static/src/xml/**/*",
        ],
    },
    "data": [],
    "demo": [],
}
