# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Company(models.Model):
    _inherit = 'res.company'

    cc_name_ar  = fields.Char("Arabic Name" )
    cc_street_ar  = fields.Char("Arabic Street")
    cc_street2_ar  = fields.Char("Arabic Street 2")
    cc_city_ar  = fields.Char("Arabic City")
    cc_state_ar  = fields.Char("Arabic State")
    cc_country_ar  = fields.Char("Arabic Country", default="المملكة العربية السعودية")