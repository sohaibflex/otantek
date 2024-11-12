# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License OPL-1 (https://www.odoo.com/documentation/14.0/legal/licenses.html).

from odoo import api, fields, models
from .product_product import FB_STATUSES


class ProductTemplate(models.Model):
    _inherit = "product.template"

    feed_fb_status = fields.Selection(
        selection=FB_STATUSES,
        string='Status',
        compute='_compute_feed_fb_status',
        inverse='_inverse_feed_fb_status',
        store=True,
    )

    @api.depends('product_variant_ids', 'product_variant_ids.feed_fb_status')
    def _compute_feed_fb_status(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_fb_status = template.product_variant_ids.feed_fb_status
        for template in (self - unique_variants):
            template.feed_fb_status = False

    def _inverse_feed_fb_status(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_fb_status = \
                    template.feed_fb_status
