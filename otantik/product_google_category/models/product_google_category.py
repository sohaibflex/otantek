# Copyright © 2021 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductGoogleCategory(models.Model):
    _name = "product.google.category"
    _description = 'Google Product Category'
    _parent_store = True
    _order = "sequence, name"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    sequence = fields.Integer(index=True)
    code = fields.Char(
        string='Code',
        required=True,
    )
    parent_id = fields.Many2one(
        comodel_name='product.google.category',
        string='Parent',
        index=True,
    )
    parent_path = fields.Char(index=True)
    child_id = fields.One2many(
        'product.google.category',
        'parent_id',
        string='Children Categories',
    )
    parents_and_self = fields.Many2many(
        'product.google.category',
        compute='_compute_parents_and_self',
    )

    @api.constrains('parent_id')
    def check_parent_id(self):
        if not self._check_recursion():
            raise ValueError(_(
                'Error ! You cannot create recursive categories.'))

    @api.constrains('code')
    def _check_code(self):
        for category in self:
            recs = self.search_count([('code', '=', category.code)])
            if recs > 1:
                raise ValidationError(_(
                    'The code of the Google category must be unique.'))

    def name_get(self):
        res = []
        for category in self:
            res.append((category.id, " > ".join(
                category.parents_and_self.mapped('name'))))
        return res

    def unlink(self):
        self.child_id.parent_id = None
        return super(ProductGoogleCategory, self).unlink()

    def _compute_parents_and_self(self):
        for category in self:
            if category.parent_path:
                category.parents_and_self = self.env['product.google.category'].browse([int(p) for p in category.parent_path.split('/')[:-1]])
            else:
                category.parents_and_self = category
