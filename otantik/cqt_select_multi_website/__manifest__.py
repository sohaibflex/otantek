# -*- coding: utf-8 -*-

{
    'name': "Multiple Websites Per Product (Select different websites in Product)",
    'version': '14.0.1.0.1',
    'sequence': 11,
    'author': 'Cronquotech',
    'support': 'cronquotech@gmail.com',
    'website': "https://cronquotech.odoo.com",
    'summary': '''
    Multiple Websites, 
    Multiple Website,
    Website,
    Product,
    Different Websites,
    Website wise Product,
    ''',
    'description': "Using this module user able to view the specific products per selected websites in product view",
    'category': 'Website',
    'depends': ['website_sale'],
    'data': [
        'views/product_template_view.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    "license": "LGPL-3",
    'price': 25.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
