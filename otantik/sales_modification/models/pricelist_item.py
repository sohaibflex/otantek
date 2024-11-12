from odoo import fields, models


class PricelistItemInherit(models.Model):
    _inherit = 'product.pricelist.item'


    def write(self, vals):
        res = super(PricelistItemInherit, self).write(vals)
        for rec in self:
            if rec.applied_on == '1_product':
                rec.product_tmpl_id.compute_discount_value()
            elif rec.applied_on == '0_product_variant':
                rec.product_tmpl_id.compute_discount_value()
            elif rec.applied_on == '2_product_category':
                all_products = self.env['product.template'].search([('categ_id','=',rec.categ_id.id)])
                all_products.compute_discount_value()
                all_variants = self.env['product.product'].search([('categ_id','=',rec.categ_id.id)])
                all_variants.compute_discount_value()
            elif rec.applied_on == '3_global':
                self.env['product.template'].search([]).compute_discount_value()
                self.env['product.product'].search([]).compute_discount_value()
        return res
