# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


# class ProductTemplateAttributeLine(models.Model):
#     _inherit = "product.template.attribute.line"

    # @api.constrains('active', 'value_ids', 'attribute_id')
    # def _check_valid_values(self):
    #     res = super(ProductTemplateAttributeLine, self)._check_valid_values()
    #     for ptal in self:
    #         if ptal.value_ids and len(ptal.value_ids) > 1:
    #             raise ValidationError(
    #                 _("Only one value can be selected!"))
    #     return res


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    inventory_availability = fields.Selection([
        ('never', 'Sell regardless of inventory'),
        ('always', 'Show inventory on website and prevent sales if not enough stock'),
        ('threshold', 'Show inventory below a threshold and prevent sales if not enough stock'),
        ('custom', 'Show product-specific notifications'),
        ('hide', "Don't Show inventory on website and prevent sales if not enough stock"),
    ], string='Inventory Availability', help='Adds an inventory availability status on the web product page.',
        default='never')

    @api.onchange('public_categ_ids')
    def onchange_public_categ_ids(self):
        """ Set domain for alternative products """
        for rec in self:
            if rec.public_categ_ids:
                product_list_ids = self.env['product.template'].search(
                    [('public_categ_ids', 'in', rec.public_categ_ids.ids), ('id', '!=', rec._origin.id)]).mapped('id')
                rec.alternative_product_ids = [(6, 0, product_list_ids)]
                return {
                    'domain': {'alternative_product_ids': [('public_categ_ids', 'in', rec.public_categ_ids.ids),
                                                           ('id', '!=', rec._origin.id)]}}
            else:
                rec.alternative_product_ids = [(5, 0, 0)]
                return {
                    'domain': {'alternative_product_ids': []}}

    @api.onchange('product_brand_ept_id')
    # @api.onchange('product_brand_ept_id','x_studio_color')
    def onchange_product_brand_ept_id(self):
        """ Set domain for accessories products """
        for rec in self:
            if rec.product_brand_ept_id:
                product_template_ids = self.env['product.brand.ept'].browse(
                    [rec.product_brand_ept_id.id]).product_ids.ids
                # if rec.x_studio_color:
                #     product_template_ids = product_template_ids.filtered(lambda x:x.x_studio_color == rec.x_studio_color)
                product_list_ids = self.env['product.product'].search(
                    [('product_tmpl_id', 'in', product_template_ids),
                     ('product_tmpl_id', '!=', rec._origin.id)]).mapped('id')
                rec.accessory_product_ids = [(6, 0, product_list_ids)]
                return {
                    'domain': {'accessory_product_ids': [('product_tmpl_id', 'in', product_template_ids),
                                                         ('product_tmpl_id', '!=', rec._origin.id)]}}
            else:
                rec.accessory_product_ids = [(5, 0, 0)]
                return {
                    'domain': {'accessory_product_ids': []}}

    def _update_alternative_products(self):
        """ Set alternative products and accessaories products """
        recs = self.env['product.template'].search([])
        for rec in recs:
            rec.sudo().onchange_product_brand_ept_id()
            rec.sudo().onchange_public_categ_ids()




