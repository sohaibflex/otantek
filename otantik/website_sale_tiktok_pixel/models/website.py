# Copyright © 2023 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    @api.model
    def _tracking_event_mapping(self, service_type):
        res = super(Website, self)._tracking_event_mapping(service_type)
        if service_type == 'tiktok_pixel':
            res = {
                'lead': 'Contact',
                'sign_up': 'CompleteRegistration',
                'view_product': 'ViewContent',
                'view_product_list': 'ViewContent',
                'search_product': 'Search',
                'add_to_wishlist': 'AddToWishlist',
                'add_to_cart': 'AddToCart',
                'begin_checkout': 'InitiateCheckout',
                'add_payment_info': 'AddPaymentInfo',
                'purchase': 'CompletePayment',
                'purchase_portal': 'CompletePayment',
            }
        return res

    def _ttp_allowed_services(self):
        self.ensure_one()
        return self.sudo().tracking_service_ids.filtered(
            lambda s: s.type == 'tiktok_pixel' and s.active
        )

    def ttp_get_keys(self):
        super(Website, self).ttp_get_keys()
        tiktok_services = self._ttp_allowed_services()
        return tiktok_services and tiktok_services.mapped('key') or []
