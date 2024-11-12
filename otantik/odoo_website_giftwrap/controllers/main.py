# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http, SUPERUSER_ID
from odoo.http import request


class OdooWebsiteGiftWrap(http.Controller):

    @http.route('/shop/cart/giftwrap', type='json', auth="public", methods=['POST'], website=True)
    def wallet(self, notes, product, **post):
        cr, uid, context = request.cr, request.uid, request.context

        order = request.website.sale_get_order()

        giftwrap = request.env['giftwrap.configuration'].sudo().browse(product)

        order_line_obj = request.env['sale.order.line'].sudo()
        flag = 1 if order.order_line.filtered(lambda x:x.product_id.id == giftwrap.product_id.id) else 0

        if flag == 0:
            res = order_line_obj.sudo().create({
                'product_id': giftwrap.product_id.id,
                'name': giftwrap.product_id.name,
                'price_unit': giftwrap.product_id.with_company(request.env.company).lst_price,
                'order_id': order.id,
                'product_uom': giftwrap.product_id.uom_id.id,
                'name': notes,
            })

        return True

    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
