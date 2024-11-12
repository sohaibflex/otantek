# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields , models,_
import base64, binascii
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import Warning ,ValidationError,UserError


class DeliveryCarrier(models.Model):
	_inherit="delivery.carrier"


	delivery_type = fields.Selection(selection_add = [('aramex','Aramex')], ondelete={'aramex': 'set default'})
	aramex_product_group = fields.Many2one(comodel_name = 'aramex.product.group', string = 'Aramex Product Group')
	aramex_product_type = fields.Many2one(comodel_name = 'aramex.product.type', string = 'Aramex Product Type')
	aramex_payment_method = fields.Many2one(comodel_name = 'aramex.payment.method', string = 'Aramex Payment Method')
	aramex_service = fields.Many2one(comodel_name = 'aramex.service',string = 'Aramex Service')


	# @api.onchange('aramex_product_group')
	# def onchange_product_group(self):
	# 	result = {}
	# 	if self.aramex_product_group and self.aramex_product_group.code == "DOM":
	# 		self.aramex_product_type = False
	# 		result['domain'] = {'aramex_product_type': [('id', 'in', self.env["aramex.product.type"].search([("code","=","OND")]).ids)]}
	# 	else :
	# 		self.aramex_product_type = False
	# 		result['domain'] = {'aramex_product_type': [('id', 'in', self.env["aramex.product.type"].search([("code","!=","OND")]).ids)]}
	# 	return result

	# @api.one
	# @api.onchange("uom_id")
	# def onchange_uom_id(self):
		# if self.delivery_type == "aramex":
			# if self.uom_id.name and self.uom_id.name.upper() in ["LB", "LB(S)"]:
				# self.delivery_uom = "LB"
			# if self.uom_id.name and self.uom_id.name.upper() in ["KG", "KG(S)"]:
				# self.delivery_uom = "KG"

	@api.model
	def create(self, vals):
		if vals.get("delivery_type", False) and vals["delivery_type"] == "aramex" and vals.get("uom_id", False):
			uom_obj = self.env["uom.uom"].browse(vals["uom_id"])
			if uom_obj and uom_obj.name.upper() not in ["LB", "LB(S)","KG", "KG(S)"]:
				raise UserError(_("Aramex Shipping support weight in KG and LB only. Select Odoo Product UoM accordingly."))
		if vals.get("delivery_type", False) and vals["delivery_type"] == "aramex" and vals.get("delivery_uom", False):
			if vals["delivery_uom"] not in ["LB","KG"]:
					raise UserError(_("Aramex Shipping support weight in KG and LB only. Select API UoM accordingly."))
		return super(DeliveryCarrier, self).create(vals)

	def write(self, vals):
		for rec in self:
			if self.delivery_type == "aramex" and vals.get("uom_id", False):
				uom_obj = self.env["uom.uom"].browse(vals["uom_id"])
				if uom_obj and uom_obj.name.upper() not in ["LB", "LB(S)","KG", "KG(S)"]:
					raise UserError(_("Aramex Shipping support weight in KG and LB only. Select Odoo Product UoM accordingly."))
			if self.delivery_type == "aramex" and vals.get("delivery_uom", False):
				if vals["delivery_uom"] not in ["LB","KG"]:
					raise UserError(_("Aramex Shipping support weight in KG and LB only. Select API UoM accordingly."))
		return super(DeliveryCarrier, self).write(vals)

class WkShippingAramexProductType(models.Model):
	_name = "aramex.product.type"
	_description = "Aramex product type"

	name = fields.Char(string = "Name", required=1)
	code = fields.Char(string = "Code", required=1)
	is_dutiable = fields.Boolean(string="Dutiable Product")
	description = fields.Text(string="Full Description")


class WkShippingAramexService(models.Model):
	_name = "aramex.service"
	_description = "Aramex Service"

	name = fields.Char(string = "Name", required=1)
	code = fields.Char(string = "Code", required=1)
	description = fields.Text(string="Full Description")

class WkShippingAramexProductGroup(models.Model):
	_name = "aramex.product.group"
	_description = "Aramex product group"

	name = fields.Char(string = "Name", required=1)
	code = fields.Char(string = "Code", required=1)
	description = fields.Text(string="Full Description")
	
class WkShippingAramexPaymentMethod(models.Model):
	_name = "aramex.payment.method"
	_description = "Aramex product method"

	name = fields.Char(string = "Name", required=1)
	code = fields.Char(string = "Code", required=1)
	description = fields.Text(string="Full Description")


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	aramex_shipping_label = fields.Char(string="Aramex Shipping Label", copy=False)
	number_of_cartons = fields.Integer('Number of cartons')

		
	def send_to_shipper(self):
		if self.carrier_id.delivery_type != "aramex":
			super(StockPicking, self).send_to_shipper()
		else:
			self.ensure_one()
			pickings = self
			context = dict(self.env.context or {})
			context['active_id'] = self.id
			context["active_model"] = "stock.picking"

			if pickings and pickings.carrier_id.delivery_type == "aramex" and not self._context.get("Testing", False):
				# if not len(self.package_ids):
				# 	raise ValidationError('Create the package first for picking %s before sending to shipper.' % (self.name))
				delivery_uom= ""
				weight = 0
				product_uom_obj = self.env['uom.uom']
				if pickings.carrier_id.delivery_uom == "KG":
					check_list = ["KG", "KG(S)", "KG(s)", "kg", "kg(S)", "kg(s)", "Kg", "Kg(S)", "Kg(s)", "KILOGRAM", "Kilogram", "kilogram"]
				if pickings.carrier_id.delivery_uom == "LB":
					check_list = ["LB", "LB(S)","LB(s)", "Lb", "LbS)","Lb(s)", "lb", "lb(s)", "lb(S)", "POUND", "Pound", "pound"]
				if check_list:
					uom_obj_for_api = product_uom_obj.search([("name", "in", check_list)], limit=1)
				items = pickings.move_lines
				if uom_obj_for_api:
					for line in items:
						q = pickings.carrier_id._get_default_uom()._compute_quantity(line.product_uom_qty, uom_obj_for_api)
						# q = product_uom_obj._compute_qty_obj(
							# pickings.carrier_id._get_default_uom(), line.product_uom_qty, uom_obj_for_api)
						weight += (line.product_id.weight or 0.0) * q

				if pickings.carrier_id.uom_id.name.upper() in ["LB", "LB(S)", "POUND"] and pickings.carrier_id.delivery_uom == "LB":
					delivery_uom = "LB"
				elif pickings.carrier_id.uom_id.name.upper() in ["KG", "KG(S)", "KILOGRAM"] and pickings.carrier_id.delivery_uom == "KG":
					delivery_uom = "KG"
				else :
					delivery_uom = pickings.carrier_id.delivery_uom

				warehouse_partner = pickings.picking_type_id.warehouse_id.partner_id
				customer = pickings.partner_id
				qty = 0
				product_desc = ""
				for ml in pickings.move_lines:
					qty += ml.product_uom_qty
					product_desc += ml.product_id.name + ", "
				service_type = ''
				cod_amount = 0
				if pickings and pickings.sale_id and pickings.sale_id.payment_term_id and pickings.sale_id.payment_term_id.is_cod:
					service_type = 'CODS'
					cod_amount = pickings.sale_id.amount_total
				vals = {
					#Sender Details
					"sender_name" : warehouse_partner.name,
					"sender_title" : warehouse_partner.title.name,
					"sender_company_name" : warehouse_partner.parent_id.name if warehouse_partner.parent_id else warehouse_partner.name if warehouse_partner else "",
					"sender_phone1" : warehouse_partner.phone,
					"sender_phone1_ext" : "",
					"sender_phone2" : "",
					"sender_phone2_ext" : "",
					# "sender_fax_number" : warehouse_partner.fax,
					"sender_mobile" : warehouse_partner.mobile,
					"sender_email" : warehouse_partner.email,
					"sender_street1" : warehouse_partner.street,
					"sender_street2" : warehouse_partner.street2,
					"sender_city" : warehouse_partner.city,
					"sender_state" : warehouse_partner.state_id.name if warehouse_partner.state_id else "",
					"sender_zip" : warehouse_partner.zip,
					"sender_country" : warehouse_partner.country_id.code,

					#Receiver Details
					"receiver_name" : customer.name,
					"receiver_title" :  customer.title.name,
					"receiver_company_name" :  customer.parent_id.name if customer.parent_id else customer.name if customer else "",
					"receiver_phone1" :  customer.phone,
					"receiver_phone1_ext" :  "",
					"receiver_phone2" :  "",
					"receiver_phone2_ext" :  "",
					# "receiver_fax_number" :  customer.fax,
					"receiver_mobile" :  customer.mobile ,
					"receiver_email" :  customer.email,
					"receiver_street1" :  customer.street,
					"receiver_street2" :  customer.street2,
					"receiver_city" :  customer.city,
					"receiver_state" :  customer.state_id.name ,
					"receiver_zip" :  customer.zip,
					"receiver_country" :  customer.country_id.code,

					#Shipment Details
					"total_weight" : weight, #pickings.carrier_id._get_weight(pickings=pickings),
					"delivery_uom" : delivery_uom,
					"total_qty" : qty,
					"comments" : "",
					"pickup_location" : "",
					"operation_instaruction" : "",
					"shipment_ref1" : pickings.name,
					"shipment_ref2" : pickings.sale_id.name,
					"product_type" : pickings.carrier_id.aramex_product_type.code,
					"service_type" : service_type,
					"payment_type" : pickings.carrier_id.aramex_payment_method.code,
					"description_of_goods" : product_desc,
					"number_of_cartons":pickings.number_of_cartons,
					"cod_amount":cod_amount,
					"cod_currency":pickings.sale_id and pickings.sale_id.currency_id and pickings.sale_id.currency_id.name or False,
					"custome_currency":pickings.sale_id and pickings.sale_id.currency_id and pickings.sale_id.currency_id.name or False,
					"insurance_currency":pickings.sale_id and pickings.sale_id.currency_id and pickings.sale_id.currency_id.name or False,

					"picking_id" : pickings.id,
				}
				view = self.env['ir.model.data'].xmlid_to_res_id('aramex_delivery_carrier.aramex_wizard_form')
				wiz_id = self.env['aramex.wizard'].create(vals)
				return {
					'name': _('Aramex Shipment'),
					'type': 'ir.actions.act_window',
					'view_type': 'form',
					'view_mode': 'form',
					'res_model': 'aramex.wizard',
					'views': [(view, 'form')],
					'view_id': view,
					'target': 'new',
					'res_id': wiz_id.id,
				}
			res = self.carrier_id.send_shipping(self)[0]
			self.carrier_price = res['exact_price']
			self.carrier_tracking_ref = res['tracking_number']
			msg = _("Shipment sent to carrier %s for expedition with tracking number %s") % (self.carrier_id.name, self.carrier_tracking_ref)
			self.message_post(body=msg)


	def get_apc_shipping_label(self,Label,Shipment):
		for record in self:
			attachments = []
			for item in range(len(Label)):
				attachments.append(('aramex_' +Shipment[item]+'.pdf', base64.b64decode(Label[item])))
				msg = "Label generated For Aramex Shipment "
				
			if attachments:
				record.message_post(body=msg, subject="Label For Aramex Shipment",attachments=attachments)
				return True
				

class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    package_carrier_type = fields.Selection(
    	selection_add=[('aramex', 'Aramex')], ondelete={'aramex': 'cascade'})
