from odoo import models, fields, api


class OrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    def compute_total_cost(self):
        for rec in self:
            rec.total_price = rec.purchase_price * rec.product_uom_qty
            # print("iii")

    # @api.depends('product_id')
    # def get_product_image(self):
    #     for rec in self:
    #         rec.image = rec.product_id.image_1920

    # seq = fields.Integer(string="Seq", readonly=True)
    total_price = fields.Float(string="Total Price", compute=compute_total_cost)
    image = fields.Binary(string="Image", related='product_id.image_1920')

    # @api.constrains('product_id')
    # def compute_sequence_line(self):
    #     order_id = self.order_id
    #     print("order id", self.order_id)
    #     order_lines = self.env['sale.order.line'].search([('order_id', '=', order_id.id)])
    #     i = 1
    #     for line in order_lines:
    #         if line.product_id:
    #             line.seq = i
    #             i += 1
        # if last_order_line:
        #     self.seq = last_order_line.seq + 1
        # else:
        #     self.seq = 1

    # @api.model
    # def create(self, vals):
    #     order_id = vals.get('order_id')
    #     last_order_line = self.env['sale.order.line'].search([('order_id', '=', order_id)], order='id desc', limit=1)
    #     if last_order_line:
    #         vals['seq'] = last_order_line.seq + 1
    #     else:
    #         vals['seq'] = 1

    # return super(OrderLineInherit, self).create(vals)

    # @api.model
    # def compute_previous_sequence(self):
    #     orders = self.env['sale.order'].search([])
    #     for order in orders:
    #         print("order id", order.id)
    #         lines = self.env['sale.order.line'].search([('order_id', '=', order.id)], order="id")
    #         i = 1
    #         for line in lines:
    #             line.seq = i
    #             print("Line seq", line.seq)
    #             line.write({'seq': line.seq})
    #             i = i + 1
    #
