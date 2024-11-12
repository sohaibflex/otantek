from odoo import models, fields, api, _


class InheritPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
