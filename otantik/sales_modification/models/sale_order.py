from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = ['sale.order']

    payment_reference = fields.Many2one('payment.acquirer', string="Payment Acquirer",store=True)
    payment_transaction_id = fields.Many2one('payment.transaction')

    customer_notes = fields.Text('Customer Notes')

    # @api.depends('transaction_ids')
    # def set_payment_ref(self):
    #     for rec in self:
    #         print('transaction ids', rec.transaction_ids)
    #         print('order name', rec.name)
    #         payment_transactions = self.env['payment.transaction'].search([])
    #         for transaction in payment_transactions:
    #             order_name = rec.name
    #             if order_name in transaction.reference:
    #                 print('order name', order_name)
    #                 print('transaction ref', transaction.reference)
    #                 rec.payment_reference = transaction.acquirer_id
    #                 rec.payment_transaction_id = transaction.id
    #                 print("transaction acquire", transaction.acquirer_id)

    # @api.depends('transaction_ids')
    # def set_payment_ref(self):
    #     for rec in self:
    #         payment_reference = False
    #         payment_transaction_id = False
    #         order_name = rec.name
    #         payment_transaction = self.env['payment.transaction'].search([('reference', 'ilike', order_name),('state','=','done')],
    #                                                                      order='id desc', limit=1)
    #         if payment_transaction and payment_transaction.acquirer_id:
    #             payment_reference = payment_transaction.acquirer_id
    #             payment_transaction_id = payment_transaction.id
    #         rec.payment_reference = payment_reference
    #         rec.payment_transaction_id = payment_transaction_id

    def change_to_fully_invoiced(self):
        for rec in self:
            rec.invoice_status = 'invoiced'

