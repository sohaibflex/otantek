# -*- coding: utf-8 -*-
{
    'name': "sales_modification",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Walaa Mostafa",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','website_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/product_template.xml',
        'views/assets.xml',
        'views/templates.xml',
        'views/sale_order.xml',
        # 'views/sale_order_line.xml',
        # 'reports/sale_order_document_inherit.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
