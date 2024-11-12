# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

from typing import Dict

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WebsiteTrackingService(models.Model):
    _inherit = "website.tracking.service"

    type = fields.Selection(
        selection_add=[('tiktok_pixel', 'TikTok Pixel')],
        ondelete={'tiktok_pixel': 'cascade'},
    )

    # flake8: noqa: E501
    @api.constrains('type', 'track_id_external', 'track_ip_address', 'track_user_agent', 'track_email', 'track_phone', 'track_country', 'track_city')
    def _check_available_visitor_data(self):
        super(WebsiteTrackingService, self)._check_available_visitor_data()
        for service in self.filtered(lambda s: s.type == 'tiktok_pixel'):
            if service.track_country or service.track_city or service.track_user_agent or service.track_ip_address:
                raise ValidationError(_('Only the following data can be sent via TikTok Pixel: Email, Phone, External ID.'))

    def get_common_data(self, event_type, product_data_list, order, pricelist):
        self.ensure_one()
        if self.type != 'tiktok_pixel':
            return super(WebsiteTrackingService, self).get_common_data(
                event_type=event_type,
                product_data_list=product_data_list,
                order=order,
                pricelist=pricelist,
            )
        data = {
            'content_type': 'product',
            'currency': self.website_id._tracking_get_currency(order=order, pricelist=pricelist).name,  # flake8: noqa: E501
        }
        return data

    def get_item_data_from_product_list(self, product_data_list, pricelist):
        self.ensure_one()
        service = self
        if service.type != 'tiktok_pixel':
            return super(WebsiteTrackingService, self).get_item_data_from_product_list(product_data_list, pricelist)
        items = []
        total_value = 0
        for product_data in product_data_list:
            product = service.get_item(product_data)
            price = product_data.get('price', 0)
            total_value += price
            item_data = {
                'content_id': '%d' % product.id,
                'price': float('%.2f' % price),
                'quantity': product_data.get('qty', 1),
                'content_name': product.name,
            }
            item_data.update(service.get_item_categories(product))
            items.append(item_data)
        items_data = {
            'value': float('%.2f' % total_value),
            'contents': items,
        }
        return items_data

    def get_item_data_from_order(self, order):
        self.ensure_one()
        service = self
        if service.type != 'tiktok_pixel':
            return super(WebsiteTrackingService, self).get_item_data_from_order(order)
        items = []
        for line in order.order_line:

            product = line.product_id
            if service.item_type == 'product.template':
                product = product.product_tmpl_id

            item_data = {
                'content_id': '%d' % product.id,
                'price': float('%.2f' % service._get_final_product_price(line)),
                'quantity': line.product_uom_qty,
                'content_name': product.name,
            }
            item_data.update(service.get_item_categories(product))
            items.append(item_data)
        data = {
            'value': float('%.2f' % order.amount_total),
            'contents': items,
        }
        return data

    def get_data_for_sign_up(self, product_data_list=None, pricelist=None, order=None):
        self.ensure_one()
        data = super(WebsiteTrackingService, self).get_data_for_sign_up(product_data_list, pricelist, order)
        if self.type == 'tiktok_pixel':
            data.update({'value': self.lead_value})
        return data

    def get_data_for_search_product(self, product_data_list, pricelist, order):
        self.ensure_one()
        data = super(WebsiteTrackingService, self).get_data_for_search_product(product_data_list, pricelist, order)
        if self.type == 'tiktok_pixel':
            data.update({'query': self._context.get('search_term', '')})
        return data

    @api.model
    def _get_privacy_url(self):
        urls = super(WebsiteTrackingService, self)._get_privacy_url()
        urls.update({'tiktok_pixel': 'https://ads.tiktok.com/i18n/official/policy/business-products-terms'})
        return urls

    def get_visitor_data(self):
        self.ensure_one()
        if self.type != 'tiktok_pixel':
            return super(WebsiteTrackingService, self).get_visitor_data()
        visitor_data = super(
            WebsiteTrackingService, self.with_context(phone_remove_plus=False)
        ).get_visitor_data()
        user_data = {}
        if visitor_data.get('external_id'):
            user_data['external_id'] = self.env['website.tracking.log']._hash_sha256(
                visitor_data.get('external_id')
            )
        if visitor_data.get('em'):
            user_data['email'] = visitor_data.get('em')
        if visitor_data.get('ph'):
            user_data['phone_number'] = visitor_data.get('ph')
        return user_data
