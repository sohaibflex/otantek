# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today  Technaureus Info Solutions(<http://technaureus.com/>).
from odoo import api, fields, models

class Product(models.Model):
    _inherit = 'product.template'
    
    cc_name_ar = fields.Char(string="الاسم بالعربي")