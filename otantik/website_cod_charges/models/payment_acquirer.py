from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang



class PaymentAcquirerTap(models.Model):
    _inherit = "payment.acquirer"

    collection_fees = fields.Float(string="Collection Fees")
    is_cod = fields.Boolean(
        string="Is COD", compute="_compute_is_cod", store=True, copy=False
    )
    product_cod_id = fields.Many2one('product.product',string='Cod Product')

    @api.onchange("payment_term_id")
    @api.depends("payment_term_id")
    def _compute_is_cod(self):
        for payment in self:
            payment.is_cod = False
            # if payment.payment_term_id and payment.payment_term_id == self.env.ref(
            #     "account.account_payment_term_immediate"
            # ):
            if payment.payment_term_id and payment.payment_term_id.is_cod:
                payment.is_cod = True
                # product_cod_id = self.env['product.product'].search([('is_cod','=',True)],limit=1)
                # if product_cod_id:
                #     payment.product_cod_id = product_cod_id
                #     payment.collection_fees = product_cod_id.lst_price

    @api.model
    def _cron_set_is_cod(self):
        payment_ids = self.env["payment.acquirer"].search([("state", "!=", "disabled")])
        for payment in payment_ids:
            payment.is_cod = False
            # if payment.payment_term_id and payment.payment_term_id == self.env.ref(
            #     "account.account_payment_term_immediate"
            # ):
            if payment.payment_term_id and payment.payment_term_id.is_cod:
                payment.is_cod = True

    @api.constrains("is_cod")
    def check_payment_is_cod(self):
        for payment in self:
            domain = [("is_cod", "=", True), ("id", "!=", payment.id)]
            if self.company_id:
                domain+=[("company_id",'=',self.company_id.id)]
            cod_payment = self.search(domain)
            if payment.is_cod and cod_payment:
                raise ValidationError(
                    _("COD Payment(%s) already exist.") % cod_payment.name
                )

    @api.model
    def format_value(self, amount, currency=False, blank_if_zero=False):
        ''' Format amount to have a monetary display (with a currency symbol).
        E.g: 1000 => 1000.0 $

        :param amount:          A number.
        :param currency:        An optional res.currency record.
        :param blank_if_zero:   An optional flag forcing the string to be empty if amount is zero.
        :return:                The formatted amount as a string.
        '''
        currency_id = currency or self.env.company.currency_id
        if currency_id.is_zero(amount):
            if blank_if_zero:
                return ''
            # don't print -0.0 in reports
            amount = abs(amount)

        if self.env.context.get('no_format'):
            return amount
        return formatLang(self.env, amount, currency_obj=currency_id)
    
class CODPaymentTerms(models.Model):
    _inherit = "account.payment.term"

    is_cod = fields.Boolean(string="Is COD", copy=False)
