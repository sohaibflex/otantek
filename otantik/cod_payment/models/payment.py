# coding: utf-8
from odoo import api, fields, models, _
class CodPayment(models.Model):
    _inherit = 'payment.acquirer'

    def manual_get_form_action_url(self):
        return '/payment/transfer/feedback'

