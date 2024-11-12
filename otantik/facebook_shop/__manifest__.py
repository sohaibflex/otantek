# Copyright © 2020 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

# flake8: noqa: E501

{
    'name': 'Odoo Facebook Catalog Integration and Odoo Instagram Feed: Unlock the Power of Social Commerce',
    'version': '14.0.3.1.0',
    'category': 'eCommerce',
    'author': 'Garazd Creation',
    'website': 'https://garazd.biz/shop',
    'license': 'OPL-1',
    'summary': 'Product catalogue to advertise or sell items on Facebook and Instagram. Data Feed | Data Import | Data Source | FB Product Catalog | Odoo Instagram Feed',
    'images': ['static/description/banner.png', 'static/description/icon.png'],
    'live_test_url': 'https://garazd.biz/r/wA6',
    'depends': [
        'product_data_feed',
        'product_google_category',
        'product_facebook_category',
        'product_data_feed_brand',
        'product_data_feed_number',
    ],
    'data': [
        'data/product_data_feed_recipient_data.xml',
        'data/product_data_feed_data.xml',
        'data/product_data_feed_column_value_data.xml',
        'data/product_data_feed_column_data.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
    ],
    'demo': [
        'demo/product_demo.xml',
        'demo/product_data_feed_demo.xml',
    ],
    'price': 45.0,
    'currency': 'EUR',
    'support': 'support@garazd.biz',
    'application': True,
    'installable': True,
    'auto_install': False,
}
