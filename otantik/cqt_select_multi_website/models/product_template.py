# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    '''Added new field for add all the websites on which you want to show this product
     leave it empty if you want to show the product in all websites'''
    website_ids = fields.Many2many('website', string="Websites",
        help="""Add here all the websites on which you want to show this product
        leave it empty if you want to show the product in all websites.
        """)
