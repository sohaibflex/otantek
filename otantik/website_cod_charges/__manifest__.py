# -*- coding: utf-8 -*-
{
    "name": "website_cod_charges",
    "summary": """
        Payment is cash on delivery then add line in SOL""",
    "description": """
        Payment is cash on delivery then add line in SOL""",
    "author": "Intalio",
    "website": "https://www.intalio.com/",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "website",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["website_sale", "website_payment_terms","payment"],
    # always loaded
    "data": [
        "data/demo.xml",
        "data/cron.xml",
        "views/payment_views.xml",
        "views/product_views.xml",
        # "views/payment_page.xml",
    ],
}
