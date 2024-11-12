

from odoo import api, fields, models

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # @api.model
    # def create(self, vals):
    #     vals['company_id'] = self.self.env.company.id
    #     record = super().create(vals)
    #     return record

class AccountMove(models.Model):
    _inherit = "account.move"

    ot_checked = fields.Boolean(string='Checked', default=False,tracking=True)
    ot_hr_je = fields.Boolean(string='HR Journal Entry', default=False,tracking=True)

    def ot_checked_button(self):
        for rec in self:
            rec.ot_checked = True

    def ot_hr_je_button(self):
        for rec in self:
            if rec.ot_hr_je :
                rec.ot_hr_je = False
            else:
                rec.ot_hr_je = True
                                        


class otCategory(models.Model):
    _name = "ot.category"
    name = fields.Char('Name', index=True, translate=True, required=True)
    code = fields.Char('Code', index=True, translate=True)
    type = fields.Selection([('collection', 'Collection'), ('color', 'Color'),('material', 'Material'), ('capacity', 'Capacity'), ('pieces', 'Pieces')],
                                     string="Type",translate=True)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.onchange('carrier_id')
    def onchange_carrier_id(self):
        self.sale_id.carrier_id = self.carrier_id.id


    @api.onchange('carrier_tracking_ref')
    def onchange_ccarrier_tracking_ref(self):

        self.sale_id.ot_carrier_tracking_ref = self.carrier_tracking_ref
        
        
class Product(models.Model):
    _inherit = "product.product"


    ot_barcode_carton = fields.Char("Barcode Carton")
    ot_volume_carton = fields.Float("Volume Carton")
    ot_collection = fields.Many2one("ot.category",string="Collection",domain="[('type', '=', 'collection')]")
    ot_color = fields.Many2one("ot.category",string="Color",domain="[('type', '=', 'color')]")
    ot_material = fields.Many2one("ot.category",string="Material",domain="[('type', '=', 'material')]")
    ot_capacity = fields.Many2one("ot.category",string="Capacity",domain="[('type', '=', 'capacity')]")
    ot_pieces = fields.Many2one("ot.category",string="Number Of Pieces",domain="[('type', '=', 'pieces')]")
    ot_weight_pound = fields.Float("Pound")
    ot_woo_category = fields.Char("Woo Category")
    ot_pic_link = fields.Char("Pic Link")


class ProductTemplate(models.Model):
    _inherit = "product.template"

    list_price = fields.Float('Sale Price', company_dependent=True, digits='Product Price', required=True, default=0.0)

    @api.depends('company_id')
    def _compute_currency_id(self):
        for template in self:
            template.currency_id = self.env.company.currency_id.id

    ot_barcode_carton = fields.Char(
        related="product_variant_ids.ot_barcode_carton", readonly=False
    )
    ot_volume_carton = fields.Float(
        related="product_variant_ids.ot_volume_carton", readonly=False
    )

    ot_collection = fields.Many2one(related="product_variant_ids.ot_collection", store=True, readonly=False,string="Collection",domain="[('type', '=', 'collection')]")
    ot_color = fields.Many2one(related="product_variant_ids.ot_color", store=True,readonly=False,string="Color",domain="[('type', '=', 'color')]")
    ot_material = fields.Many2one(related="product_variant_ids.ot_material", store=True,readonly=False,string="Material",domain="[('type', '=', 'material')]")
    ot_capacity = fields.Many2one(related="product_variant_ids.ot_capacity", store=True,readonly=False,string="Capacity",domain="[('type', '=', 'capacity')]")
    ot_pieces = fields.Many2one(related="product_variant_ids.ot_pieces", store=True,readonly=False,string="Number Of Pieces",domain="[('type', '=', 'pieces')]")
    ot_weight_pound = fields.Float(related="product_variant_ids.ot_weight_pound", readonly=False, string="pound")
    ot_woo_category = fields.Char(related="product_variant_ids.ot_woo_category", readonly=False,string="Woo Category" )
    ot_pic_link = fields.Char(related="product_variant_ids.ot_pic_link", readonly=False,string="Pic Link")

class SaleOrder(models.Model):
    _inherit = "sale.order"
    ot_carrier_id = fields.Many2one('delivery.carrier', 'Carrier')
    ot_carrier_tracking_ref = fields.Char(string='Tracking Reference')
    ot_driver_id = fields.Many2one("res.partner",string="Driver")
    ot_delivery_state = fields.Selection([('picking', 'Picking'), ('picked', 'Picked'),  ('ofd', 'Out For Delivery'),('delivered', 'Delivered'),('returned', 'Returned')], ('OT Delivery state'),track_visibility='onchange')
    ot_Payment_reference  = fields.Char(string='Payment Reference')
    
    team_id = fields.Many2one('crm.team', 'Sales Team',
        change_default=True, default=-1, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")


class ProductCategory(models.Model):
    _inherit = "product.category"
    name = fields.Char('Name', index=True, translate=True, required=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    margin = fields.Float(
        "Margin", compute='_compute_margin',
        digits='Product Price', store=True, groups="sales_team.group_sale_manager")
    margin_percent = fields.Float(
        "Margin (%)", compute='_compute_margin', store=True, groups="sales_team.group_sale_manager")
    purchase_price = fields.Float(
        string='Cost', compute="_compute_purchase_price",
        digits='Product Price', store=True, readonly=False,
        groups="sales_team.group_sale_manager")

    ot_image_128 = fields.Binary(related="product_template_id.image_128" )


