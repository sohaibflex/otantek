# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2016-Present Webkul Software Pvt. Ltd.
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

from odoo import api, models, fields, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_widget = fields.Boolean(
        string = 'Product Widget ',
        related = 'website_id.product_widget',
        readonly = False,
    )

    data_disable_installment = fields.Boolean(
        string = 'Disable Installment',
        related = 'website_id.data_disable_installment',
        readonly = False,
    )
    data_disable_paylater = fields.Boolean(
        string = 'Disable Paylater',
        related = 'website_id.data_disable_paylater',
        readonly = False,
    )

    data_payment_type = fields.Selection(
        [('paylater', 'Pay Later'), ('installment', 'Installment')], 
        related = 'website_id.data_payment_type',
        readonly = False,
        string="Payment type",
    )

    data_installment_minimum_amount = fields.Float(
        string="Installment Minimum Amount",
        related = 'website_id.data_installment_minimum_amount',
        readonly = False,
    )

    data_installment_maximum_amount = fields.Float(
        string="Installment Maximum Amount",
        related = 'website_id.data_installment_maximum_amount',
        readonly = False,
    )

    data_installment_available_amount = fields.Float(
        string="Installment Available Amount",
        related = 'website_id.data_installment_available_amount',
        readonly = False,
    )

    data_pay_later_max_amount = fields.Float(
        string="Pay Later Maximum Amount",
        related = 'website_id.data_pay_later_max_amount',
        readonly = False,
    )
    data_number_of_installments  = fields.Selection(
        [('2', 2), ('3', 3),('4',4),('5',5),('6',6),('12',12)],
        string="No of Installments",
        related = 'website_id.data_number_of_installments',
        readonly = False,
    )


    @api.onchange('data_payment_type')   
    def _onchange_data_payment_type(self):
        """If payment type will be Paylater than data installment automatically set to True and vice-versa"""
        if self.data_payment_type == 'paylater':
            self.data_disable_installment = True
            self.data_disable_paylater = False
        else:
            self.data_disable_paylater = True
            self.data_disable_installment = False

    @api.onchange('data_installment_maximum_amount')   
    def _onchange_data_installment_maximum_amount(self):
        if self.data_installment_maximum_amount < self.data_installment_minimum_amount:
            raise UserError(_('The Installation maximum amount should not be less than the Installation minimum amount.'))

    @api.onchange('data_installment_minimum_amount')   
    def _onchange_data_installment_minimum_amount(self):
        if self.data_installment_minimum_amount > self.data_installment_maximum_amount:
            raise UserError(_("The Installation minimum amount should not be greater than the Installation maximum amount."))
        elif self.data_installment_minimum_amount < 0:
            raise UserError(_("The Installation minimum amount should not be less than 0."))

