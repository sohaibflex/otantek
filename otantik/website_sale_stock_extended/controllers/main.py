from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing


class PaymentProcessingInherit(PaymentProcessing):

    @http.route()
    def payment_status_page(self, **kwargs):
        res = super().payment_status_page(kwargs=kwargs)
        tx_ids_list = self.get_payment_transaction_ids()
        payment_transaction_ids = request.env['payment.transaction'].sudo().browse(tx_ids_list).exists()
        if payment_transaction_ids.sale_order_ids and payment_transaction_ids.filtered(lambda x: x.state == 'done'):
            payment_transaction_ids.sale_order_ids[0].acquirer_reference = \
            payment_transaction_ids.filtered(lambda x: x.state == 'done')[0].acquirer_reference
        return res