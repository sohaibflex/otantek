from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_qty = fields.Float(string='Total Quantity', compute='_compute_total_qty')


    @api.depends('move_ids_without_package.product_uom_qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = sum(rec.move_ids_without_package.mapped('product_uom_qty'))

