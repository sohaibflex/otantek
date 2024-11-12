# Copyright © 2019 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

# flake8: noqa: E501

{
    'name': 'Odoo Facebook Pixel Tracking | Facebook Pixel Integration in Odoo',
    'version': '14.0.2.1.0',
    'category': 'eCommerce',
    'author': 'Garazd Creation',
    'website': 'https://garazd.biz/odoo-website-tracking',
    'license': 'OPL-1',
    'summary': 'eCommerce Facebook Pixel | Meta Pixel | Track Events | Website events tracking | Facebook Pixel Integration | Website Tracking | Add eCommerce events to product and category website pages',
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'live_test_url': 'https://garazd.biz/r/GiE',
    'depends': [
        'website_facebook_pixel',
        'website_sale_tracking_base',
    ],
    'data': [
        'views/website_templates.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [
        'data/website_tracking_service_demo.xml',
    ],
    'price': 85.0,
    'currency': 'EUR',
    'support': 'support@garazd.biz',
    'application': True,
    'installable': True,
    'auto_install': False,
}
