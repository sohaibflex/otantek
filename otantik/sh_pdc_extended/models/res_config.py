# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'


    pdc_customer_under_collection = fields.Many2one(
        'account.account', string="PDC Customer Under Collection")



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pdc_customer_under_collection = fields.Many2one('account.account', string="PDC Customer Under Collectio",
                                    related='company_id.pdc_customer_under_collection', readonly=False)


    