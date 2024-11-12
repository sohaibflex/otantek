from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_cod = fields.Boolean(string="Is COD", copy=False)

    @api.constrains("is_cod")
    def check_is_cod(self):
        for product in self:
            cod_product = self.search([("is_cod", "=", True), ("id", "!=", product.id)])
            if product.is_cod and cod_product:
                raise ValidationError(
                    _("COD Product(%s) already exist.") % cod_product.name
                )
