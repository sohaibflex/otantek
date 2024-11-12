# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

from typing import Dict

from odoo import api, fields, models
from odoo.http import request


class WebsiteTrackingService(models.Model):
    _inherit = "website.tracking.service"

    type = fields.Selection(
        selection_add=[('fbp', 'Facebook Pixel')],
        ondelete={'fbp': 'cascade'},
    )

    def get_common_data(self, event_type, product_data_list, order, pricelist):
        self.ensure_one()
        if self.type != 'fbp':
            return super(WebsiteTrackingService, self).get_common_data(
                event_type=event_type,
                product_data_list=product_data_list,
                order=order,
                pricelist=pricelist,
            )
        data = {
            'content_type': 'product',
            'currency': self.website_id._tracking_get_currency(
                order=order, pricelist=pricelist).name,
        }
        return data

    def get_item_data_from_product_list(self, product_data_list, pricelist):
        self.ensure_one()
        if self.type != 'fbp':
            return super(WebsiteTrackingService, self).get_item_data_from_product_list(
                product_data_list=product_data_list,
                pricelist=pricelist,
            )
        service = self

        items = []
        total_value = 0
        content_category = ''
        for product_data in product_data_list:
            product = service.get_item(product_data)
            price = product_data.get('price', 0)
            total_value += price
            item_data = {
                'id': '%d' % product.id,
                'quantity': product_data.get('qty', 1),
            }
            items.append(item_data)
            # Get a product category from the first product
            if not content_category:
                content_category = service.get_item_categories(product)
        items_data = {
            'value': float('%.2f' % total_value),
            'contents': items,
            'num_items': len(items),
        }
        items_data.update(content_category)
        return items_data

    def get_item_data_from_order(self, order):
        self.ensure_one()
        if self.type != 'fbp':
            return super(WebsiteTrackingService, self).get_item_data_from_order(order)
        service = self
        items = []
        for line in order.order_line:

            product = line.product_id
            if service.item_type == 'product.template':
                product = product.product_tmpl_id

            item_data = {
                'id': '%d' % product.id,
                'quantity': line.product_uom_qty,
            }
            items.append(item_data)
        data = {
            'value': float('%.2f' % order.amount_total),
            'contents': items,
            'num_items': len(items),
        }
        return data

    def get_data_for_view_product_list(self, product_data_list, pricelist, order):
        self.ensure_one()
        data = super(WebsiteTrackingService, self).get_data_for_view_product_list(
            product_data_list=product_data_list,
            pricelist=pricelist,
            order=order,
        )
        if self.type == 'fbp':
            # Value of "product_category" is sent from JS event "view_product_list"
            # as "kw" param, all "kw" params are passed through the context.
            public_category_id = self._context.get('product_category')
            public_category = self.env[
                'product.public.category'].browse(public_category_id)
            data.update({
                'content_category': public_category and public_category.name
                or 'All Products',
            })
        return data

    def get_data_for_search_product(self, product_data_list, pricelist, order):
        self.ensure_one()
        data = super(WebsiteTrackingService, self).get_data_for_search_product(
            product_data_list=product_data_list,
            pricelist=pricelist,
            order=order,
        )
        if self.type == 'fbp':
            data.update({'search_string': self._context.get('search_term', '')})
        return data

    def get_data_for_view_product(self, product_data_list, pricelist, order):
        self.ensure_one()
        data = super(WebsiteTrackingService, self).get_data_for_view_product(
            product_data_list=product_data_list,
            pricelist=pricelist,
            order=order,
        )
        if self.type == 'fbp':
            product = self.get_item(product_data_list[0])
            data.update({
                'content_name': product.name,
            })
        return data

    def get_data_for_add_to_cart(self, product_data_list, pricelist, order):
        self.ensure_one()
        data = super(WebsiteTrackingService, self).get_data_for_add_to_cart(
            product_data_list=product_data_list,
            pricelist=pricelist,
            order=order,
        )
        if self.type == 'fbp':
            product = self.get_item(product_data_list[0])
            data.update({
                'content_name': product.name,
            })
        return data

    def _fbp_get_visitor_data(self) -> Dict:
        self.ensure_one()
        visitor_data = {}
        if not request:
            return visitor_data
        visitor = \
            self.env['website.visitor']._get_visitor_from_request(force_create=False)
        if not visitor:
            return visitor_data

        service = self
        log = self.env['website.tracking.log']

        if service.track_id_external:
            visitor_data["external_id"] = visitor.access_token

        country = visitor.partner_id.country_id or visitor.country_id
        if service.track_country and country:
            visitor_data["country"] = log._hash_sha256(country.name)

        if service.track_city and visitor.partner_id.city:
            visitor_data["ct"] = log._hash_sha256(visitor.partner_id.city)

        if service.track_email and visitor.email:
            visitor_data["em"] = log._hash_email(visitor.email)

        phone = visitor.partner_id and (
            visitor.partner_id.phone or visitor.partner_id.mobile) or visitor.mobile
        if service.track_phone and phone and country:
            visitor_data["ph"] = \
                log._hash_phone_number(phone, country, remove_plus=True)
        return visitor_data

    @api.model
    def _get_privacy_url(self) -> Dict:
        urls = super(WebsiteTrackingService, self)._get_privacy_url()
        urls.update({'fbp': 'https://www.facebook.com/business/m/privacy-and-data'})
        return urls

    @api.model
    def _fields_to_invalidate_cache(self):
        res = super(WebsiteTrackingService, self)._fields_to_invalidate_cache()
        res += ['track_id_external', 'track_country', 'track_city', 'track_email',
                'track_phone']
        return res
