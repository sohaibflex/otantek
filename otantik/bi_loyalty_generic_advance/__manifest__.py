# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Advance All in one Loyalty - POS & Website Rewards Redeem Program',
    'version': '14.0.0.5',
    'category': 'eCommerce',
    'summary': 'Website Loyalty rewards pos loyalty rewards pos club membership website Loyalty Program eCommerce Loyalty Program pos customer Loyalty and Rewards Program pos Bonus Gift website Referral website reward redeem on pos rewards All in one Loyalty management',
    'description' :"""

        All in one Loyalty Management Advance in odoo,
        All in one Loyalty and Rewards Program in Odoo,
        sale loyalty and rewarads program in odoo,
        website loyalty and rewarads program in odoo,
        pos loyalty and rewarads program in odoo,
        redeem and reward loyalty points in odoo,
        loyalty points in sale website and POS,
        discounts or loyalty in sale website and POS,
        Assign Manually Loyalty Points in odoo,
        Import Loyalty Points in odoo,
        Deactive Loyalty in odoo,
        Create Tiered Loyalty Program in odoo, 

    """,
    'author': 'BrowseInfo',
    "price": 70,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','sale_management','point_of_sale','website','website_sale','delivery','website_sale_delivery','bi_loyalty_generic'],
    'data': [
        'security/ir.model.access.csv',
        'views/loyalty_view.xml',
        'views/loyalty_tier_view.xml',
        'views/res_config_view.xml',
        'views/sale_order_view.xml',
        'views/template.xml',
        'wizard/import_functionality.xml',
        'wizard/manually_loyalty.xml',
    ],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/kj1ltycy5Y0',
    "images":['static/description/Banner.png'],
}
