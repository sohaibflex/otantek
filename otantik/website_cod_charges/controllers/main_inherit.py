from odoo import http
from odoo.http import request
from odoo import _
from odoo.exceptions import ValidationError
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.portal import PaymentProcessing


# class FormAddressInherit(WebsiteSale):
#     @http.route(
#         ["/shop/confirmation"], type="http", auth="public", website=True, sitemap=False
#     )
#     def payment_confirmation(self, **post):
#         sale_order_id = request.session.get("sale_last_order_id")
#         if sale_order_id:
#             order = request.env["sale.order"].sudo().browse(sale_order_id)
#             # if order.payment_term_id and order.payment_term_id == request.env.ref(
#             #     "account.account_payment_term_immediate"
#             # ):
#             if order.payment_term_id and order.payment_term_id.is_cod:
#                 product_id = (
#                     request.env["product.product"]
#                     .sudo()
#                     .search([("is_cod", "=", True)], limit=1)
#                 )
#                 if not product_id:
#                     raise ValidationError(_("COD Product not exist."))
#                 payment_acquirer = (
#                     request.env["payment.acquirer"]
#                     .sudo()
#                     .search([("is_cod", "=", True)], limit=1)
#                 )
#                 vals = {
#                     "order_id": order.id,
#                     "product_id": product_id.id,
#                     "name": product_id.name,
#                     "product_uom": product_id.uom_id.id,
#                 }
#                 order_line = request.env["sale.order.line"].sudo().create(vals)
#                 order_line.product_id_change()
#                 order_line.product_uom_qty = 1.00
#                 order_line.price_unit = (
#                     payment_acquirer and payment_acquirer.collection_fees or 0.0
#                 )
#             return request.render("website_sale.confirmation", {"order": order})
#         else:
#             return request.redirect("/shop")

class PaymentProcessingInherit(PaymentProcessing):

    @http.route(['/payment/process'], type="http", auth="public", website=True, sitemap=False)
    def payment_status_page(self, **kwargs):
        # When the customer is redirect to this website page,
        # we retrieve the payment transaction list from his session
        res = super().payment_status_page(**kwargs)
        if res.qcontext and  res.qcontext.get('payment_tx_ids'):
            payment_transaction_ids = request.env['payment.transaction'].sudo().browse(res.qcontext.get('payment_tx_ids')).exists()
            if payment_transaction_ids and all(True if transaction.acquirer_id and transaction.acquirer_id.is_cod else False  for transaction in payment_transaction_ids ):
                sale_ids = payment_transaction_ids.sale_order_ids
                for sale in sale_ids:
                    sale.sudo().action_confirm()
        return res
