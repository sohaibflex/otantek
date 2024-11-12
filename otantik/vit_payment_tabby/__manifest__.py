# -*- coding: utf-8 -*-

{
    "name": "Tabby Payment Gateway",
    "summary": "Tabby Payment Gateway",
    "description": "Pay Securely with Tabby convenience in Odoo!",
    'author': 'VarietyIT',
    'maintainer': 'VarietyIT',
    'company': 'VarietyIT',
    'website': 'https://varietyit.com',
    'price': 250,
    'currency': 'USD',
    'license': 'LGPL-3',
    "category": "Accounting",
    "version": "14.0.1.0.0",
    "depends": ["payment", "website_sale_delivery"],
    "data": [
        "views/payment_acquirer.xml",
        "views/payment_tabby_templates.xml",
        "data/tabby_payment_data.xml",
        "views/template.xml",
        "views/res_config_settings_views.xml",
        "views/js_template.xml",
    ],

    'images': ['static/description/banner.png'],
    "application": True,
    "installable": True,
    'auto_install': False,
    "sequence": -100,
}
