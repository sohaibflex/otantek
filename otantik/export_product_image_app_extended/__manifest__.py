# -*- coding: utf-8 -*-
{
    'name': "export_product_image_app_extended",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'export_product_image_app', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/export_product_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
