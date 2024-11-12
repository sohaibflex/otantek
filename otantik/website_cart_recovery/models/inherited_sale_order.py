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
import logging

from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    followup_messages = fields.Integer(string="Number of Follow up Message Send", default=0)

    @api.model
    def website_cart_recovery_main(self, *args, **kwargs):
        domain = []
        if self._context.get('recovery_config'):
            domain += [('id', '=', self._context['recovery_config'])]
        else:
            domain += [('website_published', '=', True)]
        if kwargs.get('cron_id'):
            domain += [('cart_recovery_cron_shedular', '=', kwargs['cron_id'])]
        all_configs = self.env['cart.recovery.settings'].search(domain)
        self.default_cart_recover_email()
        for params in all_configs:
            followup_mail_count = params.followup_mail_count
            date_obj = params.start_from
            limit_date_str = fields.datetime.strftime(date_obj, DEFAULT_SERVER_DATETIME_FORMAT)

            if followup_mail_count in ['one', 'two', 'three']:
                cart_recovery_template_one_time = params.cart_recovery_template_one_time
                current_datetime = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                current_datetime = datetime.strptime(current_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                diff_datetime = current_datetime - timedelta(hours = cart_recovery_template_one_time)
                diff_datetime = diff_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                ids_for_send_mail = self.search([
                    ('create_date', '>=', limit_date_str),
                    ('is_abandoned_cart', '=', True),
                    ('write_date', '<=', diff_datetime),
                    ('followup_messages', '=', 0),
                    ('website_id', 'in', [False, params.website_id.id])
                ])
                _logger.info("==========ids_for_send_mail=============%r",ids_for_send_mail)
                ids_for_send_mail.send_cart_recovery_mail(1, params=params)

            if followup_mail_count in ['two', 'three']:
                cart_recovery_template_two_time = params.cart_recovery_template_two_time
                current_datetime = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                current_datetime = datetime.strptime(current_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                diff_datetime = current_datetime - timedelta(hours = cart_recovery_template_two_time)
                diff_datetime = diff_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                ids_for_send_mail = self.search([
                    ('create_date', '>=', limit_date_str),
                    ('is_abandoned_cart', '=', True),
                    ('write_date', '<=', diff_datetime),
                    ('followup_messages', '=', 1),
                    ('website_id', 'in', [False, params.website_id.id])
                ])
                ids_for_send_mail.send_cart_recovery_mail(2, params=params)

            if followup_mail_count in ['three']:
                cart_recovery_template_three_time =params.cart_recovery_template_three_time
                current_datetime = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                current_datetime = datetime.strptime(current_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                diff_datetime = current_datetime - timedelta(hours = cart_recovery_template_three_time)
                diff_datetime = diff_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                ids_for_send_mail = self.search([
                    ('create_date', '>=', limit_date_str),
                    ('is_abandoned_cart', '=', True),
                    ('write_date', '<=', diff_datetime),
                    ('followup_messages', '=', 2),
                    ('website_id', 'in', [False, params.website_id.id])
                ])
                ids_for_send_mail.send_cart_recovery_mail(3, params=params)

    def default_cart_recover_email(self):
        """ Default sale order cart recover email sent. """

        params = self.env['ir.config_parameter'].sudo()
        abandoned_orders = self.search([('is_abandoned_cart', '=', True), ('cart_recovery_email_sent', '=', False)])
        template_id = int(params.get_param('website_sale.cart_recovery_mail_template_id', 0))
        if template_id:
            Template = self.env['mail.template'].browse(template_id)
            for abandoned in abandoned_orders:
                mail_confirmed = Template.send_mail(abandoned.id, True)
                if mail_confirmed:
                    abandoned.write({'cart_recovery_email_sent': True})
                    _logger.info("############--Default cart recovery mail is send to following id --%r", abandoned.id)
                else:
                    _logger.info("############--Default cart recovery mail sending Failed for id --%r", abandoned.id)

    def send_cart_recovery_mail(self, msg_count = -1, params={}):
        Template = False
        if msg_count == 1:
            Template = params.cart_recovery_email_template_one
        elif msg_count == 2:
            Template = params.cart_recovery_email_template_two
        elif msg_count == 3:
            Template = params.cart_recovery_email_template_three
        if Template:

            # Template = self.env['mail.template'].browse(template_id)
            for rec in self:
                rec._portal_ensure_token()
                mail_confirmed = Template.send_mail(rec.id, True)
                if mail_confirmed:
                    rec.write( {'followup_messages': msg_count})
                    _logger.info("############--%r cart recovery mail is send to following id %r", msg_count, rec.id)
                else:
                    _logger.info("############--%r cart recovery mail sending Failed for id %r", msg_count, rec.id)
