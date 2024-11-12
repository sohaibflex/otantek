from odoo import models, fields, api, _


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_term_id = fields.Many2one('account.payment.term', readonly=False, store=True, compute="_get_payment_term")
    payment_reference = fields.Many2one('payment.acquirer', string="Payment Acquirer", store=True,
                                        compute='set_payment_ref')

    @api.depends('transaction_ids')
    def set_payment_ref(self):
        for rec in self:
            payment_reference = False
            payment_transaction_id = False
            order_name = rec.name
            payment_transaction = self.env['payment.transaction'].search(
                [('reference', 'ilike', order_name), ('state', '=', 'done'),('acquirer_id.company_id','=',rec.company_id.id)],
                order='id desc', limit=1)
            if not payment_transaction:
                payment_transaction = self.env['payment.transaction'].search(
                    [('reference', 'ilike', order_name),('acquirer_id.company_id','=',rec.company_id.id)],
                    order='id desc', limit=1)
            if payment_transaction and payment_transaction.acquirer_id:
                payment_reference = payment_transaction.acquirer_id
                payment_transaction_id = payment_transaction.id
            rec.payment_reference = payment_reference
            rec.payment_transaction_id = payment_transaction_id
            rec._get_payment_term()

    @api.depends('payment_reference')
    def _get_payment_term(self):
        for record in self:
            if record.payment_reference and record.payment_reference.payment_term_id and record.payment_transaction_id:
                record.payment_term_id = record.payment_reference.payment_term_id.id
