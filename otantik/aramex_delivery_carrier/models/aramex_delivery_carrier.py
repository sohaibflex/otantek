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
import logging
from odoo.exceptions import Warning ,ValidationError
from urllib3.exceptions import HTTPError
from datetime import datetime
_logger = logging.getLogger(__name__)
try:
	from suds.client import Client
except:
	raise Warning("Please install suds: pip3 install suds-py3")
import itertools
# import os
# 
# this_file_dir = os.path.dirname(__file__)

# rate_cal_service_url = str("file:" + this_file_dir.replace("/models", "/") +"aramex/aramex-rates-calculator-wsdl.wsdl")
rate_cal_service_url = "https://ws.aramex.net/ShippingAPI.V2/RateCalculator/Service_1_0.svc?wsdl"
# shipping_service_live_wsdl = str("file:" + this_file_dir.replace("/models","/") +"aramex/shipping-services-api-wsdl.wsdl")
shipping_service_live_wsdl = "https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc?singleWsdl"
# shipping_service_dev_wsdl = str("file:" + this_file_dir.replace("/models","/") +"aramex/shipping-services-api-dev-wsdl.wsdl")
shipping_service_dev_wsdl = "https://ws.dev.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc?singleWsdl"
#Aramex Related things
rat_cal_client = Client(rate_cal_service_url, cache=None)
aramex_tracking_link = "https://www.aramex.com/express/track-results-multiple.aspx?ShipmentNumber="


class DeliveryCarrier(models.Model):
	_inherit="delivery.carrier"

	aramex_username = fields.Char(string="User Name")
	aramex_password = fields.Char(string="Password")
	aramex_account_no = fields.Char(string="Aramex Account Number")
	aramex_account_pin = fields.Char(string="Account Pin")
	aramex_account_entity = fields.Char(string="Account Entity")
	aramex_account_country_code = fields.Char(string="Account Country Code")
	integration_level = fields.Selection(selection_add=[('fixed_rate', 'Fixed Rate')])
	
	
	def get_soap_client(self):
		# config = self._get_config(key="aramex.config.settings")
		config=self.wk_get_carrier_settings(['aramex_username','aramex_password','aramex_account_no','aramex_account_pin','aramex_account_entity','aramex_account_country_code','prod_environment'])
		if not config.get('prod_environment'):
			shipping_service_url = shipping_service_dev_wsdl
		else:
			
			shipping_service_url = shipping_service_live_wsdl
		return Client(shipping_service_url, cache=None)

	# @api.model
    # def aramex_create_package(self, order=None, picking=None, currency=None):
    #     self.wk_validate_data(order=order, pickings=picking)
    #     packaging_obj = self.env['product.packaging']
	# 	package_data = False
    #     weight_unit = self.delivery_uom
    #     if order:
    #         package_items = self.wk_get_order_package(order=order)
    #         items = self.wk_group_by('packaging_id', package_items)
    #         for order_packaging_id, wk_package_ids in items:
    #             packaging_id = packaging_obj.browse(order_packaging_id)
    #             packaging_code = packaging_id.shipper_package_code
    #             for package_id in wk_package_ids:
    #                 package_data = dict(
    #                     weight_unit=weight_unit,
    #                     currency=currency,
    #                     name=order.name,
    #                     description=order.name + ' ' + packaging_id.name,
    #                     ups_delivery_confirmation=self.ups_delivery_confirmation
    #                 )
    #                 package_data.update(package_id)
    #                 _logger.info("order package_data===%r====="%(package_data))
    #                 package_data['weight'] = self._get_api_weight(package_data.get('weight'))
    #                 package_data['packaging_code'] = packaging_code
    #                 # root_node.append(sdk.construct_package_xml(package_data))
    #     elif picking:
    #         packaging_ids = self.wk_group_by_packaging(pickings=picking)
    #         total_package = 0
    #         for packaging_id, package_ids in packaging_ids.items():
    #             packaging_code = packaging_id.shipper_package_code
    #             total_package += len(package_ids)
    #             for package_id in package_ids:
    #                 package_data = dict(weight_unit=weight_unit,currency=currency,)
    #                 pck_data = package_id.read(
    #                     ['description', 'name', 'shipping_weight', 'cover_amount', 'ups_delivery_confirmation'])
    #                 pkg_data = packaging_id.read(['height', 'width', 'length'])
    #                 package_data.update(pck_data[0])
    #                 package_data.update(pkg_data[0])
    #                 _logger.info("package_data===%r====="%(package_data))
    #                 package_data['packaging_code'] = packaging_code
    #                 package_data['weight'] = self._get_api_weight(package_data.get('shipping_weight'))
    #                 # root_node.append(sdk.construct_package_xml(package_data))
    #         picking.number_of_packages = total_package
    #     return package_data

	def create_aramex_address(self, partner_id):
		ctx = dict(self._context)
		partner_type = ctx["partner_type"] if ctx.get("partner_type") else False
		aramex_address_obj = self.get_soap_client().factory.create('Address')
		if not partner_id:
			return aramex_address_obj
		aramex_address_obj.Line1 = ctx["vals_for_shipping"]['%s_street1' % partner_type] if partner_type else partner_id.street.strip() if partner_id.street else ""
		aramex_address_obj.Line2 = ctx["vals_for_shipping"]['%s_street2' % partner_type] if partner_type else partner_id.street2.strip() if partner_id.street2 else ""
		aramex_address_obj.Line3 = ctx["vals_for_shipping"]['%s_street3' % partner_type] if partner_type else ""
		aramex_address_obj.City = ctx["vals_for_shipping"]['%s_city' % partner_type] if partner_type else  partner_id.city
		aramex_address_obj.StateOrProvinceCode = ctx["vals_for_shipping"]['%s_state' % partner_type] if partner_type else   partner_id.state_id.code
		aramex_address_obj.PostCode = ctx["vals_for_shipping"]['%s_zip' % partner_type] if partner_type else partner_id.zip
		aramex_address_obj.CountryCode = ctx["vals_for_shipping"]['%s_country' % partner_type] if partner_type else  partner_id.country_id.code
		return aramex_address_obj

	def create_aramex_dimensions(self, order=None, pickings=None, packaging_id=None, package=None):              # enter dimension for packages 
		ctx = dict(self._context)
		aramex_dimensions_obj = self.get_soap_client().factory.create('Dimensions')
		if order :
			package_items = self.wk_get_order_package(order=order)
			items=self.wk_group_by('packaging_id',package_items)
			length = 0
			width = 0
			height = 0
			for Dict in package_items:
				height = Dict['height'] if Dict.get('height',False) and height<Dict['height'] else 1
				width = Dict['width'] if Dict.get('width',False) and width<Dict['width'] else 1
				length = Dict['length'] if Dict.get('length',False) and width<Dict['length'] else 1
			aramex_dimensions_obj.Length = length
			aramex_dimensions_obj.Width = width
			aramex_dimensions_obj.Height = height
			aramex_dimensions_obj.Unit = 'IN' if self.delivery_uom == 'LB' else 'CM'
		elif ctx.get('vals_for_shipping',False) and ctx['vals_for_shipping']['sender_multi_ship']:
			aramex_dimensions_obj.Length = int(package.length) or 1
			aramex_dimensions_obj.Width = int(package.width)	or 1
			aramex_dimensions_obj.Height = int(package.height)	or 1
			aramex_dimensions_obj.Unit = 'IN' if self.delivery_uom == 'LB' else 'CM'
		else:
			aramex_dimensions_obj.Length = ctx['vals_for_shipping']['consienment_length'] or 1						# to be fetched from send to shipper wizard
			aramex_dimensions_obj.Width = ctx['vals_for_shipping']['consienment_width'] or 1
			aramex_dimensions_obj.Height = ctx['vals_for_shipping']['consienment_height'] or 1
			aramex_dimensions_obj.Unit = 'IN' if self.delivery_uom == 'LB' else 'CM'

		return aramex_dimensions_obj
	
	def create_aramex_weight(self, order=None, pickings=None, packaging_id=None, package=None):			# here to change the weight of shipmenet as per the package 
		weight = 0
		ctx = dict(self._context)
		aramex_weight_obj = self.get_soap_client().factory.create('Weight')
		if not order and not pickings:
			return aramex_weight_obj
		product_uom_obj = self.env['uom.uom']
		items = order.order_line if order else pickings.move_lines
		for line in items:
			if order and line.state == 'cancel':
				continue
			if order and (not line.product_id or line.is_delivery):
				continue
			q = self._get_default_uom()._compute_quantity(line.product_uom_qty, self.uom_id)
			# q = product_uom_obj._compute_qty_obj(
				# self._get_default_uom(), line.product_uom_qty, self.uom_id)
			weight += (line.product_id.weight or 0.0) * q
		if ctx.get("vals_for_shipping", False):
			aramex_weight_obj.Unit = ctx["vals_for_shipping"]["delivery_uom"] if ctx["vals_for_shipping"]["delivery_uom"] else self.delivery_uom
			if ctx["vals_for_shipping"]["total_weight"]:
				aramex_weight_obj.Value = package.weight if pickings and package else ctx["vals_for_shipping"]["total_weight"]
			else:
				raise Warning(_("Product weight must be greater than zero."))
		else:
			aramex_weight_obj.Unit = self.delivery_uom
			if weight :
				aramex_weight_obj.Value = weight
			else:
				raise Warning(_("Product weight must be greater than zero."))
		return aramex_weight_obj

	def get_total_cover_amount(self,order=None):
		amount = 0
		package_items = self.wk_get_order_package(order=order)
		items=self.wk_group_by('packaging_id',package_items)
		for Dict in package_items:
			amount+= Dict['wk_cover_amount'] if Dict.get('wk_cover_amount',False) else 0
		
		return amount
	
	
	
	def create_aramex_amount(self, amount_type, order=None,package=None):       #  Need to update for multiple shipments only 
		ctx = dict(self._context)
		aramex_amount_obj = self.get_soap_client().factory.create('Money')
		if amount_type == "CashOnDeliveryAmount" :
			aramex_amount_obj.Value = ctx["vals_for_shipping"]["cod_amount"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["cod_amount"] else 0.0
			aramex_amount_obj.CurrencyCode = ctx["vals_for_shipping"]["cod_currency"] if ctx.get("vals_for_shipping", False) else "USD" # For Cash on delivery, the currency must be in USD
		elif amount_type == "InsuranceAmount" :
			aramex_amount_obj.Value = package.cover_amount if package else ctx["vals_for_shipping"]["insurance_amount"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["insurance_amount"] else self.get_total_cover_amount(order=order) if order else 0.0 
			aramex_amount_obj.CurrencyCode = ctx["vals_for_shipping"]["insurance_currency"] or self.company_id.currency_id.name if ctx.get("vals_for_shipping", False) else self.company_id.currency_id.name
		elif amount_type == "CustomsValueAmount" :
			aramex_amount_obj.Value = ctx["vals_for_shipping"]["custom_amount"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["custom_amount"] else 0.0
			aramex_amount_obj.CurrencyCode = ctx["vals_for_shipping"]["custome_currency"] or self.company_id.currency_id.name if ctx.get("vals_for_shipping", False) else self.company_id.currency_id.name
		else:
			aramex_amount_obj.Value = 0.0
			aramex_amount_obj.CurrencyCode = self.company_id.currency_id.name
		return aramex_amount_obj

	def create_aramex_shipment_item(self, order=None, pickings=None, packaging_id=None, package=None):              # made changes by extracting values from packages not from pickings 
		ctx = dict(self._context)
		aramex_items_obj = self.get_soap_client().factory.create('ShipmentItem')
		if not order and not pickings:
			return aramex_items_obj
		aramex_items_obj.PackageType = 'Box'
		qty = 0
		items = order.order_line if order else pickings.move_lines
		for line in items:
			if line.product_id.type in ["consu", 'product']:
				qty += line.product_uom_qty
			
		pick_quantity=0
		if package and pickings:
			quant_ids=package.read(['quant_ids'])[0]['quant_ids']
			for quant_id in quant_ids:
				pick_quantity += self.env['stock.quant'].browse([quant_id]).quantity

		aramex_items_obj.Quantity = pick_quantity if pickings and package else ctx["vals_for_shipping"]["total_qty"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["total_qty"] else qty
		aramex_items_obj.Comments = ctx["vals_for_shipping"]["comments"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["comments"] else "There is no comments."
		aramex_items_obj.Reference = ""
		if order:
			aramex_items_obj.Weight = ctx["vals_for_shipping"]["total_weight"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["total_weight"] else self.create_aramex_weight(order=order)
		else :
			aramex_items_obj.Weight = self.create_aramex_weight(pickings=pickings, packaging_id=packaging_id, package=package) if package and packaging_id else ctx["vals_for_shipping"]["total_weight"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["total_weight"] else self.create_aramex_weight(pickings=pickings)

		return aramex_items_obj

	def create_aramex_shipment_details(self, order=None, pickings=None, packaging_ids=None, packaging_id=None, package=None):   # here to add the package data except picking data
		ctx = dict(self._context)
		aramex_shipment_details_obj = self.get_soap_client().factory.create('ShipmentDetails')

		#Removed extra attributes from suds class ShipmentDetails
		aramex_shipment_details_obj.__contains__('PieceDimensions') and delattr(aramex_shipment_details_obj,'PieceDimensions')
		aramex_shipment_details_obj.__contains__('IsTrue') and delattr(aramex_shipment_details_obj,'IsTrue')

		if not order and not pickings:
			return aramex_shipment_details_obj
		aramex_shipment_details_obj.Dimensions = self.create_aramex_dimensions(order=order, pickings=pickings, packaging_id=packaging_id, package=package)      	#   Arguments transfer for package     Need to discuss in case of single shipment
		aramex_shipment_details_obj.ActualWeight = self.create_aramex_weight(order=order) if order else self.create_aramex_weight(pickings=pickings, packaging_id=packaging_id, package=package)    # data to be fetched from package		
		aramex_shipment_details_obj.ChargeableWeight = self.create_aramex_weight(order=order) if order else self.create_aramex_weight(pickings=pickings, packaging_id=packaging_id, package=package)
		aramex_shipment_details_obj.ProductGroup = self.aramex_product_group.code if self.aramex_product_group else "EXP"
		aramex_shipment_details_obj.ProductType = ctx["vals_for_shipping"]["product_type"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["product_type"] else self.aramex_product_type.code if self.aramex_product_type else "PDX"
		aramex_shipment_details_obj.PaymentType  = ctx["vals_for_shipping"]["payment_type"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["payment_type"] else  self.aramex_payment_method.code if self.aramex_payment_method else "P"
		aramex_shipment_details_obj.PaymentOptions = ""
		aramex_shipment_details_obj.Services  = ctx["vals_for_shipping"]["service_type"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["service_type"] else ""
		# aramex_shipment_details_obj.NumberOfPieces = 1 if order else 1 if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["sender_multi_ship"] else sum([len(packages) for packaging,packages in packaging_ids.items()]) if ctx.get("vals_for_shipping", False) and packaging_ids  else 1     # need to approve
		aramex_shipment_details_obj.NumberOfPieces = ctx.get('vals_for_shipping').get('number_of_cartons') if ctx.get('vals_for_shipping') and ctx.get('vals_for_shipping').get('number_of_cartons') else 1
		aramex_shipment_details_obj.DescriptionOfGoods  = ctx["vals_for_shipping"]["description_of_goods"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["description_of_goods"] else "Goods description is not defined."
		aramex_shipment_details_obj.GoodsOriginCountry  = self.env.user.country_id.code
		aramex_shipment_details_obj.CashOnDeliveryAmount = self.create_aramex_amount(amount_type="CashOnDeliveryAmount")
		aramex_shipment_details_obj.InsuranceAmount = self.create_aramex_amount(amount_type="InsuranceAmount" ,order=order, package=package)   	# need to update
		aramex_shipment_details_obj.CustomsValueAmount = self.create_aramex_amount(amount_type="CustomsValueAmount")
		aramex_shipment_details_obj.CashAdditionalAmount = self.create_aramex_amount(amount_type="CashAdditionalAmount")
		aramex_shipment_details_obj.CollectAmount = self.create_aramex_amount(amount_type="CollectAmount")
		aramex_shipment_details_obj.Items = self.create_aramex_shipment_item(order=order) if order else self.create_aramex_shipment_item(pickings=pickings, packaging_id=packaging_id, package=package) if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["sender_multi_ship"] else list(itertools.chain(*[[self.create_aramex_shipment_item(pickings=pickings, packaging_id=packaging_id, package=package) for package in packages] for packaging_id,packages in packaging_ids.items()]))# need to update this also  for picking           # here to make changes for multiple packages.
		return aramex_shipment_details_obj

	def create_aramex_transaction(self, order=None, pickings=None):
		ctx = dict(self._context)
		aramex_transaction_obj = self.get_soap_client().factory.create('Transaction')
		if not order and not pickings:
			return aramex_transaction_obj
		aramex_transaction_obj.Reference1 = order.name if order else pickings.name
		aramex_transaction_obj.Reference2 = ''
		aramex_transaction_obj.Reference3 = ''
		aramex_transaction_obj.Reference4 = ''
		aramex_transaction_obj.Reference5 = ''

		return aramex_transaction_obj

	def create_aramex_client_info(self):
		# config = self._get_config(key="aramex.config.settings")
		config=self.wk_get_carrier_settings(['aramex_username','aramex_password','aramex_account_no','aramex_account_pin','aramex_account_entity','aramex_account_country_code','prod_environment'])
		aramex_client_info_obj = self.get_soap_client().factory.create('ClientInfo')
		aramex_client_info_obj.AccountCountryCode = config.get('aramex_account_country_code')
		aramex_client_info_obj.AccountEntity = config.get('aramex_account_entity')
		if not config.get('prod_environment') and self._context.get("called_by_rate_calculator", False):
			pass
		else:
			aramex_client_info_obj.AccountNumber = config.get('aramex_account_no')
			aramex_client_info_obj.AccountPin = config.get('aramex_account_pin')
		aramex_client_info_obj.UserName = config.get('aramex_username')
		aramex_client_info_obj.Password = config.get('aramex_password')
		aramex_client_info_obj.Version = '1.0'
		return aramex_client_info_obj

	def create_aramex_contact(self, partner_id):
		ctx = dict(self._context)
		contact_type = ctx["contact_type"] if ctx.get("contact_type", False) else False
		aramex_contact_obj = self.get_soap_client().factory.create('Contact')
		if not partner_id:
			return aramex_contact_obj
		aramex_contact_obj.Department = ""
		aramex_contact_obj.PersonName  = ctx["vals_for_shipping"]['%s_name' % contact_type] if contact_type else partner_id.name
		aramex_contact_obj.Title = ctx["vals_for_shipping"]['%s_title' % contact_type] if contact_type else partner_id.title.name
		aramex_contact_obj.CompanyName = ctx["vals_for_shipping"]['%s_company_name' % contact_type] if contact_type else partner_id.parent_id.name if partner_id.parent_id else "Odoo"
		aramex_contact_obj.PhoneNumber1 = ctx["vals_for_shipping"]['%s_phone1' % contact_type] if contact_type else partner_id.phone
		aramex_contact_obj.PhoneNumber1Ext = ctx["vals_for_shipping"]['%s_phone1_ext' % contact_type] if contact_type else ""
		aramex_contact_obj.PhoneNumber2  = ctx["vals_for_shipping"]['%s_phone2' % contact_type] if contact_type else ""
		aramex_contact_obj.PhoneNumber2Ext = ctx["vals_for_shipping"]['%s_phone2_ext' % contact_type] if contact_type else ""
		aramex_contact_obj.CellPhone = ctx["vals_for_shipping"]['%s_mobile' % contact_type] if contact_type else partner_id.mobile
		aramex_contact_obj.EmailAddress = ctx["vals_for_shipping"]['%s_email' % contact_type] if contact_type else partner_id.email
		aramex_contact_obj.Type = ""

		return aramex_contact_obj

	def create_aramex_party(self, partner_id):
		# Used for shipper and Consignee
		# config = self._get_config(key="aramex.config.settings")
		
		config=self.wk_get_carrier_settings(['aramex_username','aramex_password','aramex_account_no','aramex_account_pin','aramex_account_entity','aramex_account_country_code','prod_environment'])
		ctx = dict(self._context)
		party_type = ctx["party_type"] if ctx.get("party_type", False) else False
		aramex_party_obj = self.get_soap_client().factory.create('Party')
		if not partner_id:
			return aramex_party_obj
		aramex_party_obj.Reference1 = ctx["vals_for_shipping"]['%s_name' % party_type] if party_type else partner_id.name
		aramex_party_obj.Reference2 = partner_id.ref or ""
		if party_type == 'sender':
			aramex_party_obj.AccountNumber = config.get('aramex_account_no')
		else:
			aramex_party_obj.AccountNumber = ""
		aramex_party_obj.PartyAddress = self.with_context(partner_type = party_type).create_aramex_address(partner_id)
		aramex_party_obj.Contact = self.with_context(contact_type = party_type).create_aramex_contact(partner_id)
		return aramex_party_obj

	def create_aramex_shipment(self, order=None, pickings=None, packaging_ids=None, packaging_id=None, package=None):
		ctx = dict(self._context)
		now = datetime.now().strftime("%Y-%m-%d")
		aramex_shipment_obj = self.get_soap_client().factory.create('Shipment')
		if not order and not pickings:
			return aramex_shipment_obj
		aramex_shipment_obj.Shipper = self.with_context(party_type="sender").create_aramex_party(pickings.picking_type_id.warehouse_id.partner_id)
		aramex_shipment_obj.Consignee = self.with_context(party_type="receiver").create_aramex_party(pickings.partner_id)
		aramex_shipment_obj.Reference1 = ctx["vals_for_shipping"]["shipment_ref1"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["shipment_ref1"] else pickings.name if pickings else order.picking_ids[0].name if order.picking_ids else "No Picking For" + order.name
		aramex_shipment_obj.Reference2 = ctx["vals_for_shipping"]["shipment_ref2"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["shipment_ref2"] else pickings.sale_id.name if pickings else order.name
		aramex_shipment_obj.Reference3 = ""
		aramex_shipment_obj.TransportType_x0020_ = 0
		aramex_shipment_obj.ShippingDateTime = now
		aramex_shipment_obj.DueDate = now
		aramex_shipment_obj.PickupLocation = ctx["vals_for_shipping"]["pickup_location"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["pickup_location"] else "Reception"  #Need to discuss
		aramex_shipment_obj.PickupGUID = ''
		aramex_shipment_obj.Comments = ctx["vals_for_shipping"]["comments"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["comments"] else 'No comments define'
		aramex_shipment_obj.AccountingInstrcutions = ''
		aramex_shipment_obj.OperationsInstructions = ctx["vals_for_shipping"]["operation_instaruction"] if ctx.get("vals_for_shipping", False) and ctx["vals_for_shipping"]["operation_instaruction"] else ''
		aramex_shipment_obj.Details = self.create_aramex_shipment_details(order=order) if order else self.create_aramex_shipment_details(pickings=pickings, packaging_id=packaging_id, package=package) if ctx.get("vals_for_shipping", False) and ctx['vals_for_shipping']['sender_multi_ship'] else self.create_aramex_shipment_details(pickings=pickings, packaging_ids=packaging_ids)
		return aramex_shipment_obj

	def create_aramex_array_of_shipment(self, order=None, pickings=None, packaging_ids=None):
		ctx = dict(self._context)
		aramex_array_of_shipment_obj = self.get_soap_client().factory.create('ArrayOfShipment')
		if not order and not pickings:
			return aramex_array_of_shipment_obj
		if order:
			aramex_array_of_shipment_obj.Shipment = [self.create_aramex_shipment(order=order)]
		else:
			aramex_array_of_shipment_obj.Shipment = [self.create_aramex_shipment(pickings=pickings,packaging_ids=packaging_ids)] if not ctx["vals_for_shipping"]['sender_multi_ship'] else list(itertools.chain(*[[self.create_aramex_shipment(pickings=pickings, packaging_id=packaging_id ,package=package) for package in packages] for packaging_id , packages in packaging_ids.items()]))
		return aramex_array_of_shipment_obj

	def create_aramex_label_info(self, report_type="RPT"):
		ctx = dict(self._context)
		aramex_label_info_obj = self.get_soap_client().factory.create('LabelInfo')
		#original report id was 9202
		aramex_label_info_obj.ReportID = 9729
		aramex_label_info_obj.ReportType = report_type  #Can be 'URL' or 'RPT'
		return aramex_label_info_obj

	def aramex_set_shipping_price(self, order=None, pickings=None):
		# Code for rate calculatio
		history = None
		rate= None
		website_id = self._context.get('website_id')
		if self.delivery_type == "aramex":
			try:
				if order and order.partner_id or website_id:
					recipient = order.partner_shipping_id if order.partner_shipping_id else order.partner_id
					#history_res = self.wk_get_history_hash(order = order , partner = recipient)
					#_logger.info("--------history_res-----%r-------", history_res)
					#history = history_res.get('history')
					#_logger.info("--------history=-----%r-------",
					#			[history.available, history.price])
					#if history and  history_res.get('match'):
					#	available = history.available
					#	if not available:
					#		_logger.info("-----------History not avalibale----------")
							# raise Warning('Service not available.')
					#	if history.price:
					#		history.price
					if self.integration_level == 'fixed_rate':
						price = self.product_id.list_price
						if order.partner_id.state_id and order.partner_id.state_id.shipping_amount:
							price = order.partner_id.state_id.shipping_amount
						return price

					warehouse = order.warehouse_id
					ShipDate = datetime.now().strftime("%Y-%m-%d")
					weight_value = self._get_weight(order=order)

					# Origin Address (Shipper / Origination)
					origin_address = self.create_aramex_address(warehouse.partner_id)

					#Destination Address (Receipt / Customer)
					destinatio_address = self.create_aramex_address(recipient)

					shipmentDetails_obj = self.create_aramex_shipment_details(order=order)

					transactionobj = self.create_aramex_transaction(order=order)
					Live_clientobj = self.with_context(called_by_rate_calculator=True).create_aramex_client_info()
					rate = rat_cal_client.service.CalculateRate(Live_clientobj, transactionobj,origin_address, destinatio_address, shipmentDetails_obj)
					
					if rate.TotalAmount.CurrencyCode and rate.TotalAmount.Value:
						price = rate.TotalAmount.Value
						CurrencyCode = rate.TotalAmount.CurrencyCode
						if self.integration_level == 'fixed_rate':
							price = self.product_id.list_price
							if order.partner_id.state_id and order.partner_id.state_id.shipping_amount:
								price = order.partner_id.state_id.shipping_amount
						if history:
							history.write(dict(price = price, currency = CurrencyCode, available=True))
						return price
					else:

						raise Warning(rate)

				else:
					if pickings and pickings.partner_id:
						recipient = pickings.partner_id
						warehouse = pickings.location_id.get_warehouse()
						ShipDate=datetime.now().strftime("%Y-%m-%d")
						weight_value =self._get_weight(pickings=pickings)

						# Origin Address (Shipper / Origination)
						origin_address = self.create_aramex_address(warehouse.partner_id)

						#Destination Address (Receipt / Customer)
						destinatio_address = self.create_aramex_address(recipient)

						shipmentDetails_obj = self.create_aramex_shipment_details(pickings=pickings)

						transactionobj = self.create_aramex_transaction(pickings=pickings)
						Live_clientobj = self.create_aramex_client_info()

						rate = rat_cal_client.service.CalculateRate(Live_clientobj, transactionobj,origin_address, destinatio_address, shipmentDetails_obj)
						
						if rate.TotalAmount.CurrencyCode and rate.TotalAmount.Value:
							return rate.TotalAmount.Value
						else:
							raise Warning(rate)
			except HTTPError as e:
				_logger.info("---HTTPError---in---Aramax-rate-calculation----%r-------------------", e)
				raise Warning(e)
			except Exception as e:
				if rate:
					if (dict(rate).get('Notifications',False)):
						raise ValidationError(rate.Notifications.Notification[0].Message)
					else:
						raise ValidationError(e)	
				else:
					raise ValidationError(e)

	def aramex_rate_shipment(self, orders):
		response = {
			"price": self.aramex_set_shipping_price(order=orders) or 0,
			"error_message": None,
			"warning_message": None,
			"success": True,
		}
		return response

	def aramex_send_shipping(self, pickings):
		for obj in self:
			now = datetime.now().strftime("%Y-%m-%d")
			ctx = obj._context.copy()
			error_msg =""
			packaging_ids = obj.wk_group_by_packaging(pickings=pickings)
			ctx['vals_for_shipping']['sender_multi_ship']
			try:
				Shipments_obj = obj.create_aramex_array_of_shipment(pickings=pickings,packaging_ids=packaging_ids)
				clientobj = obj.create_aramex_client_info()
				transactionobj = obj.create_aramex_transaction(pickings.sale_id)
				labelinfoobj = obj.create_aramex_label_info('RPT')
				# _logger.info("----- %r ---- %r ------- %r ------- %r",clientobj, transactionobj, Shipments_obj, labelinfoobj)
				result = obj.get_soap_client().service.CreateShipments(clientobj, transactionobj, Shipments_obj, labelinfoobj)
				shipment_id = []
				Labels = []
				if result.Shipments:
					for ship in result.Shipments.ProcessedShipment:
						shipment_id.append(str(ship.ID))
						label_url = ship.ShipmentLabel.LabelFileContents if ship.ShipmentLabel else ""
						Labels.append(label_url)

						if label_url:
							pickings.label_genrated = True
							pickings.aramex_shipping_label = label_url

					if Labels:
						pickings.get_apc_shipping_label(Labels,shipment_id)

				
				if result.HasErrors:
					if result.Shipments:
						for x in result.Shipments.ProcessedShipment[0].Notifications.Notification:
							error_msg += x.Code + " " + x.Message + "\n"
					else:
						for x in result.Notifications.Notification:
							error_msg += x.Code + " " + x.Message + "\n"
				if error_msg:
					raise Warning(error_msg)
				total_weight = 0
				for ship_weight in Shipments_obj.Shipment:
					total_weight += ship_weight.Details.ActualWeight.Value
				shipping_weight_value = total_weight
				shipping_weight_uom = Shipments_obj.Shipment[0].Details.ActualWeight.Unit
				for product_uom_obj in obj.env["uom.uom"].search([]):
					if shipping_weight_uom == "LB" and product_uom_obj.name.upper() in ["LB", "LB(S)"] :
						pickings.shipment_uom_id = product_uom_obj
					if shipping_weight_uom == "KG" and product_uom_obj.name.upper() in  ["KG", "KG(S)"]:
						pickings.shipment_uom_id = product_uom_obj

				pickings.weight_shipment = float(shipping_weight_value)

				result = {
					'exact_price':  obj.aramex_set_shipping_price(order=pickings.sale_id) if pickings.sale_id else obj.aramex_set_shipping_price(pickings=pickings),
					'tracking_number': (','.join(shipment_id)),
				}
				return [result]
			except HTTPError as e:
				_logger.info(
					"---HTTPError---in---Aramax-send-shipping----%r-------------------", e)
				raise Warning(e)
			except Exception as e:
				_logger.info(
					"---Exception---in---Aramax-send-shipping----%r-------------------", e)
				raise Warning(e)

	@api.model
	def aramex_get_tracking_link(self,pickings):
		track_url = aramex_tracking_link + pickings.carrier_tracking_ref
		return track_url

	def aramex_cancel_shipment(self,pickings):
		raise ValidationError('This feature is not supported by Aramex.....')

class CODPaymentTerms(models.Model):
    _inherit = "account.payment.term"

    is_cod = fields.Boolean(string="Is COD", copy=False)
