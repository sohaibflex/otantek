from odoo import api, fields, models, _


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    shipping_amount = fields.Float('Shipping Amount')
