# -*- coding: utf-8 -*-
{
    'name': "Website Sale Stock Extended",

    'summary': """
       Modified Product Template     
        """,

    'author': "Techultra Solutions Pvt. Ltd.",
    'website': "https://www.techultrasolutions.com/",
    'category': 'Uncategorized',
    'version': '14.0',

    'depends': ['website_sale_stock', 'payment'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_cron.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/website_assent_inherit.xml',
        'views/sale_order_views.xml',
        'report/sale_portal_templates.xml',
        # 'report/sale_report_templates.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
