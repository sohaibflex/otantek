# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    discount_value = fields.Float('Discount',store=True,compute="compute_discount_value")

    @api.depends('list_price')
    def compute_discount_value(self):
        for record in self:
            # price_list = self.env.website.pricelist_id.item_ids.filtered(lambda a:a.product_tmpl_id.id == record.id)
            combination = record._get_first_possible_combination()
            current_website = self.env['website'].get_current_website()
            pricelist = current_website.pricelist_id
            combination_info = record._get_combination_info(combination, add_qty= 1, pricelist=pricelist)
            diff = round(record.list_price - combination_info['price'],2)
            lst_price = record.list_price if record.list_price > 0 else 0
            discount = 0 if record.list_price <=0 else round(diff*100/lst_price)
            record.discount_value = discount
