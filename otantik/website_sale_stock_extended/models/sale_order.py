from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrderInheritNew(models.Model):
    _inherit = 'sale.order'

    x_studio_payment_status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('in_payment', 'Paid (Not Reconciled)'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed Payment'),
    ])

    x_studio_delivery_tracking_number = fields.Char('Delivery Tracking Number')
    acquirer_reference = fields.Char('Acquirer Reference')


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sale_orders = self.env['sale.order'].sudo().browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'delivered':
            moves = sale_orders._create_invoices(final=self.deduct_down_payments)
            for order in sale_orders:  # added
                moves.sudo().write({'acquirer_reference': order.acquirer_reference})  # added
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                amount, name = self._get_advance_details(order)

                if self.product_id.invoice_policy != 'order':
                    raise UserError(
                        _('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(
                        _("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                taxes = self.product_id.taxes_id.filtered(
                    lambda r: not order.company_id or r.company_id == order.company_id)
                tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

                so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
                so_line = sale_line_obj.create(so_line_values)
                move = self._create_invoice(order, so_line, amount)
                move.sudo().write({'acquirer_reference': order.acquirer_reference})  # added
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}


class StockPickingInheritNew(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('carrier_tracking_ref')
    def _onchange_carrier_tracking_ref(self):
        """ Set tracking reference on sale order. """
        for rec in self:
            rec.sale_id.x_studio_delivery_tracking_number = rec.carrier_tracking_ref


class AccountMove(models.Model):
    _inherit = "account.move"

    acquirer_reference = fields.Char('Acquirer Reference')
