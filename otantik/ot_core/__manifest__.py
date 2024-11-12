# -*- coding: utf-8 -*-
{
    'name': "ot_core",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ccTech",
    'website': "http://ccsstech.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'sale_management',
        'sale_margin',
        'sale_order_line_sequence',
        'product',
        'stock',
        'sale_stock_picking_note',
        'sale_stock',
    ],

    # always loaded
    'data': [
        'views/views.xml',
        'report/report.xml',
        'security/security_group.xml',
        'security/ir.model.access.csv',
    ],

}
