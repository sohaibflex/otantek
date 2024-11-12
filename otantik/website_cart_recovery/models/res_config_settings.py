# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

mail_count = [('none', 'None'),
              ('one','One'),
              ('two','Two'),
              ('three','Three')]

class CartRecoverySettings(models.Model):
    _name = 'cart.recovery.settings'

    def _get_default_cart_recovery_cron_shedular(self):
        try:
            return self.env.ref('website_cart_recovery.ir_cron_cart_recovery').id
        except ValueError:
            return False

    def _get_default_cart_recovery_email_template_one(self):
        try:
            return self.env.ref('website_cart_recovery.website_cart_recovery_email_template_one').id
        except ValueError:
            return False

    def _get_default_cart_recovery_email_template_two(self):
        try:
            return self.env.ref('website_cart_recovery.website_cart_recovery_email_template_two').id
        except ValueError:
            return False

    def _get_default_cart_recovery_email_template_three(self):
        try:
            return self.env.ref('website_cart_recovery.website_cart_recovery_email_template_three').id
        except ValueError:
            return False

    name = fields.Char(string='Name', default="Abandoned Cart Recovery")
    followup_mail_count = fields.Selection(mail_count, string = 'Extra Follow up Mail Count', default='none', help = """Number of mails to be send for follow up.""")
    cart_recovery_cron_shedular = fields.Many2one('ir.cron','Cron Settings', required=True, default=lambda self: self._get_default_cart_recovery_cron_shedular())

    cart_recovery_email_template_one = fields.Many2one('mail.template','First Follow up Email Template', default=lambda self: self._get_default_cart_recovery_email_template_one())
    cart_recovery_template_one_time =  fields.Integer(string='Send Email After (Hour)')

    cart_recovery_email_template_two = fields.Many2one('mail.template','Secound Follow up Email Template', default=lambda self: self._get_default_cart_recovery_email_template_two())
    cart_recovery_template_two_time =  fields.Integer(string='Send Email After (Hour)')

    cart_recovery_email_template_three = fields.Many2one('mail.template','Third Follow up Email Template', default=lambda self: self._get_default_cart_recovery_email_template_three())
    cart_recovery_template_three_time =  fields.Integer(string='Send Email After (Hour)')
    start_from = fields.Date(string="Start date", required=True)
    website_id = fields.Many2one('website', string='Website', required=True)
    website_published = fields.Boolean(string='Active')


    def change_published_settings(self):
        records = self.sudo().search([
            ('website_id', '=', self.website_id.id),
            ('website_published', '=', True),
            ('id', '!=', self.id)
        ])
        for conf in records:
            conf.website_published = False


    @api.model
    def create(self, vals):
        res = super(CartRecoverySettings, self).create(vals)
        if res.start_from < fields.date.today():
            raise ValidationError("Start Date must be today's onward")
        if res.website_published:
            res.change_published_settings()
        return res


    # @api.multi
    def write(self, vals):
        res = super(CartRecoverySettings, self).write(vals)
        for record in self:
            if record.start_from < fields.date.today():
                raise ValidationError("Start Date must be today's onward")
            if record.website_published:
                record.change_published_settings()
        return res


    # @api.multi
    def cron_run(self):
        for record in self:
            cron_id = record.cart_recovery_cron_shedular
            if cron_id:
                cron_id.with_context(recovery_config=record.id).method_direct_trigger()
        return True
