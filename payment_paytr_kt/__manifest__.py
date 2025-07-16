# Part of Kitayazilim. See LICENSE file for full copyright and licensing details.

{
    "name": "Payment Provider: PayTR iFrame",
    "version": "1.2",
    "category": "Accounting/Payment Providers",
    "sequence": 350,
    "summary": "A PayTR payment provider.",
    "author": "Kıta",
    "website": "kitayazilim.com",
    "depends": ["payment", "account_payment", "sale"],
    "data": [
        "data/payment_provider_data.xml",
        "views/payment_provider_views.xml",
    ],
    "application": False,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "assets": {
        "web.assets_frontend": [
            "payment_paytr_kt/static/src/js/payment_form.js",
        ],
    },
    "license": "LGPL-3",
    "images": [
        "static/description/PayTR_kita.png",
    ],
}
