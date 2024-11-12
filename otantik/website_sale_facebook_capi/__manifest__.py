# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

{
    'name': 'Odoo Facebook Conversions API | Meta Conversion API Integration',
    'version': '14.0.1.0.0',
    'category': 'eCommerce',
    'author': 'Garazd Creation',
    'website': 'https://garazd.biz/odoo-website-tracking',
    'license': 'OPL-1',
    'summary': 'Meta Facebook Conversions API | Facebook Conversion API | Meta CAPI for Tracking Events | Facebook CAPI Integration',
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'live_test_url': 'https://garazd.biz/r/mtF',
    'depends': [
        'website_sale_facebook_pixel',
    ],
    'data': [
        'data/ir_cron_data.xml',
        'views/website_tracking_service_views.xml',
    ],
    'price': 150.0,
    'currency': 'EUR',
    'support': 'support@garazd.biz',
    'application': True,
    'installable': True,
    'auto_install': False,
}
