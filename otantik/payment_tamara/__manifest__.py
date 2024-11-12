# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

{
    "name":  "Tamara Payment Connect",
    "summary":  "Tamara Payment Connect",
    "category":  "Accounting",
    "version":  "1.0.5",
    "sequence":  1,
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    "website":  "https://store.webkul.com/",
    "description":  """Tamara Payment Connect""",
    "live_test_url":'https://odoodemo.webkul.com/?module=payment_tamara&version=14.0',
    "depends":  [
          'payment'
        , 'website_sale'
    ],
    "data":  [
        'views/payment_acquirer.xml',
        'views/payment_tamara_templates.xml',
        'data/tamara_payment_data.xml',
        'views/template.xml',
        'views/res_config_settings_views.xml'
    ],
    "images":  ['static/description/Banner.gif'],
    "application":  True,
    "installable":  True,
    "price":  199,
    "currency":  "USD",
    "pre_init_hook":  "pre_init_check",
    "post_init_hook":  "create_missing_journal_for_acquirers",
    "external_dependencies":  {"python" : ["jwt"]},
}
