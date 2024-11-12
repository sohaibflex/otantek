from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleExtended(WebsiteSale):

    @http.route(['/shop/gift'], type='http', auth="public", website=True, sitemap=False)
    def shop_gift_note(self, gift_note, **post):
        redirect = post.get('r', '/shop/cart')
        sale_order = request.website.sale_get_order()
        if gift_note:
            sale_order.sudo().write({'customer_notes':gift_note})
        return request.redirect(redirect)



# class SalesModification(http.Controller):
#     @http.route('/sales_modification/sales_modification/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_modification/sales_modification/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_modification.listing', {
#             'root': '/sales_modification/sales_modification',
#             'objects': http.request.env['sales_modification.sales_modification'].search([]),
#         })

#     @http.route('/sales_modification/sales_modification/objects/<model("sales_modification.sales_modification"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_modification.object', {
#             'object': obj
#         })
