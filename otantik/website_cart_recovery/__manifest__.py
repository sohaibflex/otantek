# -*- coding: utf-8 -*-
#################################################################################
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
#################################################################################
{
  "name"                 :  "Website Abandoned Cart Recovery",
  "summary"              :  """The module helps you to send reminder emails to the customer about their abandoned shopping cart on the website.""",
  "category"             :  "Website",
  "version"              :  "1.2.4",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Abandoned-Cart-Recovery.html",
  "description"          :  """Odoo Website Abandoned Cart Recovery
Send reminder mails to customers
Abandoned website cart
abandoned cart email
Follow-up email
Abandoned shopping cart""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_cart_recovery",
  "depends"              :  [
                             'website_sale',
                             'sale_management',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/website_cart_recovery_edi.xml',
                             'data/cart_recovery_settings_cron.xml',
                             'views/res_config_settings_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  59,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
