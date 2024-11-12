# Copyright © 2020 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License OPL-1 (https://www.odoo.com/documentation/14.0/legal/licenses.html).

import pytz

from datetime import timedelta
from typing import List

from lxml import etree as ET  # nosec
from lxml import html as HTML  # nosec
from lxml.html import clean  # nosec
from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval

from odoo import _, api, fields, models

TEXT_TYPES = ['char', 'text', 'html', 'selection']
DIGIT_TYPES = ['float', 'monetary', 'integer']
RELATION_TYPES = ['many2one']
MULTI_RELATION_TYPES = ['many2many', 'one2many']
FIELDS_DOMAIN = [
    ('ttype', 'in', TEXT_TYPES + DIGIT_TYPES + RELATION_TYPES + MULTI_RELATION_TYPES),
]
COLUMN_TYPES = [
    ('text', 'Text'),
    ('field', 'Model Field'),
    ('value', 'Value'),
    ('special', 'Special'),
]


class ProductDataFeedColumn(models.Model):
    _name = "product.data.feed.column"
    _description = 'Product Data Feed Column'
    _order = 'sequence'

    @api.model
    def _get_installed_languages(self):
        langs = self.env['res.lang'].with_context(active_test=True).search([])
        return "[('id', 'in', %s)]" % langs.ids

    sequence = fields.Integer(string='Sequence', default=100)
    name = fields.Char(required=True)
    feed_id = fields.Many2one(
        comodel_name='product.data.feed',
        string='Feed',
        ondelete='cascade',
        required=True,
    )
    recipient_id = fields.Many2one(related='feed_id.recipient_id')
    type = fields.Selection(
        selection=COLUMN_TYPES,
        string='Type',
        default='text',
        required=True,
    )
    special_type = fields.Selection(
        selection=[('multi_field', 'Multi Fields'),
                   ('price', 'Product Price'),
                   ('sale_price', 'Discounted Price'),
                   ('sale_price_effective_date', 'Discounted Price Effective Dates'),
                   ('price_currency', 'Price Currency'),
                   ('link', 'Product Link'),
                   ('image_link', 'Image Link'),
                   ('additional_image_link', 'Additional Image Links'),
                   ('all_image_link', 'All Image Links'),
                   ('availability', 'Product Availability'),
                   ('stock', 'Qty in Stock'),
                   ('availability_date', 'Product Availability Date'),
                   ('product_attribute', 'Product Attribute'),
                   ('product_attribute_multi', 'Product Attributes'),
                   ('product_weight', 'Product Weight'),
                   ('product_type', 'Public category hierarchy'),
                   ('product_tax', 'Product Tax Structure'),
                   ('price_with_tax', 'Product Price (with Taxes)'),
                   ('price_wo_tax', 'Product Price (without Taxes)')])
    value = fields.Char(string='Text Value')
    model_id = fields.Many2one(related='feed_id.model_id')
    model_name = fields.Char(string="Model Name", related='feed_id.model_id.model')
    product_attribute_id = fields.Many2one(
        comodel_name='product.attribute',
        string='Attribute',
    )
    product_attribute_ids = fields.Many2many(
        comodel_name='product.attribute',
        string='Attributes',
        help='Handle only these selected attributes. If not selected, handle all.'
    )
    with_product_attribute_name = fields.Boolean(default=False)
    # FIXME: add onchange method for the field_id if it has type 'many2one' -
    #        to check is this model has the field 'name', use 'display_name' instead
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        ondelete='cascade',
    )
    field_ttype = fields.Selection(related='field_id.ttype')
    # TODO: Add an alternative field if the primary doesn't have value
    field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        string='Available Fields',
        help='Technical field for a domain',
        compute='_compute_field_ids',
    )
    relation_model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Relation Model',
        compute='_compute_relation_model_id',
    )
    relation_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Relation Field',
        help='Field of the relation field, if you have selected '
             'the field with the type "many2one".',
    )
    value_id = fields.Many2one(
        comodel_name='product.data.feed.column.value',
        string='Value',
        ondelete='set null',
    )
    multi_value_type = fields.Selection(
        selection=[
            ('string', 'String with separator'),
            ('list', 'List'),
            ('list_of_dict', 'List of Dictionary'),
        ],
        help='Specify the type for multi values.\n"list" is used to get values '
             '(field "name") from Many2many and One2many fields.',
    )
    multi_field_name = fields.Char(string='Field Name')
    multi_field_names = fields.Char(
        string='Field Names',
        help='Field names separated by comma. For example: "name,currency_id,amount".'
    )
    multi_field_values_are_required = fields.Boolean(
        string='Values are Required',
        default=True,
    )
    multi_field_format = fields.Char(
        string='Value Format',
        help='Field value format should contain placeholders for all fields. For '
             'example: "%(field_name_1)s - %(field_name_2)d / %(field_name_3).2f".',
    )
    multi_value_separator = fields.Char(
        string='Multi Value Separator',
        default=',',
        help='Specify which separator use to divide values in the string.',
    )
    multi_limit = fields.Integer(string='Multi value Limit')
    multi_index = fields.Integer(
        string='Value Index',
        help='Value index from multi value list. Should starts from 1. '
             'Specify it if you need only one value from the list.',
    )
    multi_domain = fields.Char(
        string='Domain',
        help='Specify domain to restrict Many2many and One2many fields.',
        default='[]',
    )
    multi_dict_key = fields.Char(
        string='Dict Key',
        help='This param is used for the multi value type "List of Dictionary" '
             'to specify the repeated dict key name.',
    )
    multi_dict_value = fields.Char(
        string='Dict Value',
        help='This param is used for the multi value type "List of Dictionary" '
             'to specify the repeated dict value name.',
    )
    multi_dict_keys = fields.Char(
        string='Dict Keys',
        help='This param is used for the multi value type "List of Dictionary" '
             'to specify the repeated dict key names, separated by comma. '
             'For example: "country,rate,amount".',
    )
    multi_suffix = fields.Selection(
        selection=[('number', 'Numbered (from 0)')],
        string='Suffix',
    )
    format = fields.Char(help='The format for the field value.')
    format_force_empty_string = fields.Boolean(help='Use empty string for zero values.')
    escape_html = fields.Boolean(default=True)
    limit = fields.Integer()
    is_required = fields.Boolean(string='Required', readonly=True)
    feed_warning = fields.Char(string='Warning', copy=False)
    description = fields.Char(help='Column Description')
    language_id = fields.Many2one(
        comodel_name='res.lang',
        domain=lambda self: self._get_installed_languages(),
        help="The language that will be used to translate this column value.",
    )
    image_url_is_unique = fields.Boolean(string="URL with Checksum")
    is_cdata = fields.Boolean('CDATA', help='Put a value in the CDATA format.')
    file_type = fields.Selection(related='feed_id.file_type')
    active = fields.Boolean(default=True)

    @api.depends('field_id', 'feed_id.model_id')
    def _compute_relation_model_id(self):
        for column in self:
            if column.type == 'field' \
                    and column.field_id.ttype in RELATION_TYPES + MULTI_RELATION_TYPES:
                column.relation_model_id = self.env['ir.model'].search([
                    ('model', '=', column.field_id.relation)])[:1].id
            else:
                column.relation_model_id = None

    @api.depends('type', 'feed_id.model_id')
    def _compute_field_ids(self):
        for column in self:
            if column.type == 'field':
                domain = [('model_id', '=', column.model_id.id)]
                domain += FIELDS_DOMAIN
                available_fields = self.env['ir.model.fields'].search(domain)
                column.field_ids = [(6, 0, available_fields.ids)]
            else:
                column.field_ids = None

    def name_get(self):
        return [(rec.id, "%s (%s%s)" % (
            rec.name,
            rec.type,
            ': %s' % rec.value if rec.type == 'text'
            else ': %s' % rec.field_id.field_description if rec.type == 'field'
            else ': %s' % rec.value_id.name if rec.type == 'value'
            else ': %s' % rec.special_type if rec.type == 'special'
            else '',
        )) for rec in self]

    def _format_date_value(self, value):
        """Convert date to string with using the format from the "format" column field.

        :param string value: datetime value in the Odoo "Date" or "Datetime" format
        :return: formatted date string
        """
        self.ensure_one()
        tz = pytz.timezone(self.feed_id.tz)
        date_with_tz = tz.localize(fields.Datetime.from_string(value), is_dst=None)
        return date_with_tz.strftime(self.format or '%Y-%m-%d')

    def _format_value(self, value):
        self.ensure_one()
        res = ''
        column = self

        if isinstance(value, list):
            res = [self._format_value(li) for li in value]
            if column.multi_value_type == 'string':
                separator = column.multi_value_separator or ','
                res = separator.join(res)

        elif value:
            if column.format:
                if column.field_id.ttype in ['date', 'datetime']:
                    res = column._format_date_value(value)
                else:
                    res = ('%s' % column.format) % value
            else:
                if column.field_id.ttype == 'boolean':
                    res = 'true'
                else:
                    res = '%s' % value
        else:
            # Handle empty values
            if column.format_force_empty_string:
                res = ''
            elif isinstance(value, float):
                res = column.format and (('%s' % column.format) % 0.0) or '0.0'
            elif column.field_id.ttype == 'boolean':
                res = 'false'

        return res

    def get_product_image_url(self, product) -> str:
        self.ensure_one()
        feed = self.feed_id
        return '%(base_url)s/web/image/%(model)s/%(id)d/%(field)s%(checksum)s' % {
            'base_url': feed._get_base_url(),
            'model': feed.model_name,
            'id': product.id,
            'field': feed._get_product_image_field_name(),
            'checksum': '%s' % (self.image_url_is_unique and '/%s' % feed._get_image_checksum(product[feed._get_product_image_field_name()] or b'') or ''),  # flake8: noqa: E501
        }

    def get_product_extra_image_urls(self, product) -> List:
        self.ensure_one()
        feed = self.feed_id
        image_links = []
        images = feed.model_name == 'product.product' \
            and product.product_variant_image_ids \
            or product.product_template_image_ids
        for image in images:
            image_links.append(
                "%(base_url)s/web/image/product.image/%(id)d/%(field)s%(checksum)s" %
                ({
                    'base_url': feed._get_base_url(),
                    'id': image.id,
                    'field': feed._get_product_image_field_name(),
                    'checksum': '%s' % (self.image_url_is_unique and '/%s' % feed._get_image_checksum(image[feed._get_product_image_field_name()]) or ''),  # flake8: noqa: E501
                })
            )
        return image_links

    def get_special_value(self, product) -> str:
        """Proceed special column values. """
        self.ensure_one()
        column = self
        feed = column.feed_id
        value = ''

        if column.special_type == 'price':
            value = column._get_price_value(product)

        elif column.special_type == 'sale_price':
            if not feed.sale_pricelist_id:
                if not column.feed_warning:
                    column.feed_warning = _('The sale pricelist is not set.')
            else:
                value = column._get_price_value(product,
                                                pricelist=feed.sale_pricelist_id)

        elif column.special_type == 'sale_price_effective_date':
            pricelist = feed.sale_pricelist_id
            if pricelist:
                price_data = pricelist._compute_price_rule([(product, 1, None)])
                rule_id = price_data[product.id][1]
                rule = self.env['product.pricelist.item'].browse(rule_id)
                if rule and (rule.date_start or rule.date_end):
                    date_start = rule.date_start or fields.Date.today()
                    # If date_end is not specified we set it as + 30 days from today
                    date_end = rule.date_end or fields.Date.today() + timedelta(days=30)
                    value = "%s/%s" % (column._format_date_value(date_start),
                                       column._format_date_value(date_end))

        elif column.special_type == 'price_currency':
            value = feed.get_currency().name

        elif column.special_type == 'multi_field':
            try:
                values = {}
                for field_name in column.multi_field_names.split(","):
                    split_field_name = field_name.split('|')
                    # Many2one fields
                    if len(split_field_name) > 1:
                        field_name = split_field_name[0]
                        related_field_name = split_field_name[1]
                        record = getattr(product, field_name)
                        field_value = getattr(record, related_field_name)
                    # Simple fields
                    else:
                        field_value = getattr(product, field_name)
                    if column.multi_field_values_are_required and not field_value:
                        # Do not calculate value if all field values are required
                        values = {}
                        break
                    values[field_name] = field_value
                if values:
                    value = column.multi_field_format % values

            except Exception as e:
                column.feed_warning = _(
                    'Some field name is incorrect. Error: %s') % str(e)

        elif column.special_type == 'link':
            value = '%s%s' % (feed._get_base_url(), product.website_url)

        elif column.special_type == 'image_link':
            value = column.get_product_image_url(product)

        elif column.special_type == 'additional_image_link':
            value = column._format_value(column.get_product_extra_image_urls(product))

        elif column.special_type == 'all_image_link':
            image_urls = [column.get_product_image_url(product)]
            image_urls += column.get_product_extra_image_urls(product)
            value = column._format_value(image_urls)

        elif column.special_type in ['availability', 'stock']:
            qty = feed._get_product_qty(product)
            if column.special_type == 'availability':
                value = feed._get_availability_value(qty, column)
            elif column.special_type == 'stock':
                value = column._format_value(qty if qty > 0 else 0.0)

        elif column.special_type == 'availability_date':
            if feed.out_of_stock_mode == 'order' and not feed._get_product_qty(product):
                if product.sale_delay:
                    availability_date = fields.Datetime.to_string(
                        fields.Date.today() + timedelta(days=product.sale_delay))
                    value = self._format_date_value(availability_date)
                else:
                    if not column.feed_warning:
                        column.write({
                            'feed_warning': _('Specify the "Customer Lead Time" in '
                                              'some products that are not in stock .')})

        elif column.special_type == 'product_weight':
            weight = column._get_field_value(product, field_name='weight', to_str=True)
            value = "%s %s" % (weight, product.weight_uom_name)

        elif column.special_type == 'product_type':
            category = product.public_categ_ids[:1]
            category_names = []
            if feed.product_root_category:
                category_names.append(feed.product_root_category)
            for cat in category.parents_and_self:
                category_names.append(cat.name)
            value = ' > '.join(category_names[:5])

        elif column.special_type == 'product_attribute' and feed.model_name == 'product.product':
            values = product.product_template_attribute_value_ids.filtered(
                lambda av: av.attribute_id == column.product_attribute_id
            )
            value = values and values[:1].product_attribute_value_id.name or ''

        elif column.special_type == 'product_attribute_multi':
            # flake8: noqa: E501
            attr_value_list = []
            attr_value_list_of_dict = []
            attribute_values = self._get_product_variant(product).product_template_attribute_value_ids
            available_attributes = column.product_attribute_ids or attribute_values.attribute_line_id.mapped('attribute_id')
            for av in attribute_values.filtered(lambda av: av.attribute_line_id.attribute_id in available_attributes):
                attr_value_list_of_dict.append({av.attribute_line_id.attribute_id.name: av.name})
                if column.with_product_attribute_name:
                    attr_value_list.append(f'{av.attribute_line_id.attribute_id.name}:{av.name}')
                else:
                    attr_value_list.append(f'{av.name}')

            if column.multi_value_type == 'list':
                value = attr_value_list
            elif column.multi_value_type == 'string':
                value = column._format_value(attr_value_list)
            # In other cases we consider the type 'list_of_dict' as default
            else:
                value = attr_value_list_of_dict

        elif column.special_type == 'product_tax':
            value = [{
                'country': tax.company_id.country_id.code,
                'rate': "%.2f" % tax.amount,
            } for tax in product.taxes_id] if product.taxes_id else []

        elif column.special_type in ['price_with_tax', 'price_wo_tax']:
            price = column._get_price_value(product, with_tax=False, to_str=False)
            if product.taxes_id:
                taxes = product.taxes_id.compute_all(
                    price,
                    currency=column.feed_id.get_currency(),
                    quantity=1,
                    product=product,
                    partner=False,
                )
                if column.special_type == 'price_with_tax':
                    value = column._format_value(taxes['total_included'])
                else:
                    value = column._format_value(taxes['total_excluded'])

        return value

    def _get_product_variant(self, product):
        self.ensure_one()
        return product.product_variant_id \
            if self.feed_id.model_name == 'product.template' else product

    def _get_product_template(self, product):
        self.ensure_one()
        return product.product_tmpl_id \
            if self.feed_id.model_name == 'product.product' else product

    def _get_related_field_value(self, record, field_name='name'):
        self.ensure_one()
        column = self
        relation_field = column.relation_field_id.name
        return getattr(record, relation_field) if column.relation_field_id \
            else getattr(record, field_name)

    def _get_field_value(self, product, field_name=None, to_str=True):
        self.ensure_one()
        column = self
        value = ''
        if not (field_name or column.field_id):
            if not column.feed_warning:
                column.feed_warning = _('You need to specify the field name.')
            return value
        field_name = field_name or column.field_id.name

        if column.field_id.ttype in RELATION_TYPES:
            record = getattr(product, field_name)
            if record:
                value = column._get_related_field_value(record)

        elif column.field_id.ttype in MULTI_RELATION_TYPES:
            records = getattr(product, field_name)
            # Apply domain
            records = records.search(
                [('id', 'in', records.ids)] + safe_eval(column.multi_domain))
            values = []
            field_name = column.multi_field_name or 'name'
            for record in records:
                values.append(column._get_related_field_value(record, field_name))
            value = column.multi_limit and values[:column.multi_limit] or values
            if column.multi_index:
                list_item = value[column.multi_index-1:column.multi_index]
                value = list_item and list_item[0] or ''

        else:
            value = getattr(product, field_name)

            if value and column.field_id.ttype == 'html':
                body = HTML.fromstring("<body>%s</body>" % value)
                body.make_links_absolute(column.feed_id._get_base_url(),
                                         resolve_base_href=True)
                value = HTML.tostring(clean.clean_html(body))
                value = value.decode().replace('\n', '')
                if column.escape_html:
                    value = html_escape(value)
                    value = value.replace("'", "&apos;")  # Escape apostrophe as well

        if to_str:
            value = column._format_value(value)

        return value

    def _get_price_value(self, product, price_field='lst_price', with_currency=True,
                         with_tax=True, pricelist=None, to_str=True):
        self.ensure_one()
        column = self
        currency = column.feed_id.currency_id
        price_field = 'list_price' if price_field == 'lst_price' \
            and column.feed_id.model_name == 'product.template' else price_field

        pricelist = pricelist or column.feed_id.pricelist_id

        # Get "list price" of product variant, if there is no pricelist
        if not pricelist:
            value = self._get_field_value(product, field_name=price_field, to_str=False)

        # Get price from the pricelist
        else:
            currency = pricelist.currency_id

            # Note: Set a feed pricelist to operate with Tax Included/Excluded
            # Taxes Included
            if with_tax and self.env.user.has_group(
                    'account.group_show_line_subtotals_tax_included'):
                product_template = (
                    product if column.feed_id.model_name == 'product.template'
                    else product.product_tmpl_id)
                combination_info = product_template._get_combination_info(
                        product_id=product.id,
                        pricelist=pricelist,
                        only_template=True
                        if column.feed_id.model_name == 'product.template' else False,
                )
                value = combination_info['price']

            # Tax Excluded
            else:
                value = pricelist.get_product_price(product, 0, False)

        # Convert to string and implement the format
        if to_str:
            value = column._format_value(value)

            # Add currency code
            if with_currency and column.feed_id.currency_position != 'none':
                before = column.feed_id.currency_position == 'before' \
                    or column.feed_id.currency_position == 'default' \
                    and currency.position == 'before'
                if before:
                    value = '%s %s' % (currency.name, value)
                else:
                    value = '%s %s' % (value, currency.name)

        return value

    def _get_value(self, product):
        """Return a column value.

        :param product: instance of the "product.template" or
                                        "product.product" models
        :return: value string or CDATA
        """
        self.ensure_one()
        column = self

        value = ''
        limit = column.limit

        if column.language_id:
            product = product.with_context(lang=column.language_id.code)

        if column.type == 'text':
            value = column.value

        elif column.type == 'field':
            value = column._get_field_value(product)

        elif column.type == 'value':
            value = column.value_id.name

        elif column.type == 'special':
            value = column.get_special_value(product)

        # Post-processing
        if limit:
            value = value[:limit]

        if column.is_cdata and column.feed_id.file_type == 'xml':
            value = ET.CDATA(value or '')

        return value
