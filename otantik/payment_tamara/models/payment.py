# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import json
import requests
import hashlib
import logging
import pprint

from werkzeug import urls
from datetime import datetime
from odoo import models, api, fields, _
from odoo.tools.float_utils import float_round, float_compare
from odoo.exceptions import ValidationError, UserError
from odoo.addons.payment_tamara.controllers.main import PaymentTamaraController

_logger = logging.getLogger(__name__)


class PaymentTamaraConnect(models.Model):
    _inherit = "payment.acquirer"

    APIEND = {
        "test_url": "https://api-sandbox.tamara.co",
        "live_url": "https://api.tamara.co",
    }

    provider = fields.Selection(selection_add=[(
        'tamara', 'Tamara')], ondelete={'tamara': 'set default'})
    tamara_merchant_token = fields.Char(string="Tamara Merchant Token")
    tamara_notification_token = fields.Char(string="Tamara Notification Token")
    tamara_order_id = fields.Char(string="Tamara Order ID")
    tamara_reference_id = fields.Char(string="Tamara Reference ID")

    def _get_feature_support(self):
        res = super(PaymentTamaraConnect, self)._get_feature_support()
        res['authorize'].append('tamara')
        return res

    def _get_tamara_consumer_data(self, tamara_txn_values):
        consumer_data = dict()
        consumer_data['first_name'] =tamara_txn_values.get('billing_partner_first_name')[:51] if tamara_txn_values.get(
            'billing_partner_first_name') else "User" 
        consumer_data['last_name'] = tamara_txn_values.get(
            'billing_partner_last_name') and tamara_txn_values.get('billing_partner_last_name')[:51]
        consumer_data['phone_number'] = tamara_txn_values.get(
            'billing_partner_phone') and tamara_txn_values.get('billing_partner_phone')[:33]
        consumer_data['email'] = tamara_txn_values.get(
            'billing_partner_email') and tamara_txn_values.get('billing_partner_email')[:129]
        return consumer_data

    def _get_tamara_shipping_address(self, tamara_txn_values):
        shipping_address = dict()
        shipping_address['first_name'] = tamara_txn_values.get(
            'billing_partner_first_name') or 'User'
        shipping_address['last_name'] = tamara_txn_values.get(
            'billing_partner_last_name')
        shipping_address['line1'] = tamara_txn_values.get(
            'billing_partner').street and tamara_txn_values.get('billing_partner').street[:129]
        shipping_address['line2'] = tamara_txn_values.get(
            'billing_partner').street2 and tamara_txn_values.get('billing_partner').street2[:129]
        shipping_address['postal_code'] = tamara_txn_values.get(
            'billing_partner_zip')
        shipping_address['city'] = tamara_txn_values.get(
            'billing_partner_city')
        shipping_address['country_code'] = tamara_txn_values.get(
            'billing_partner_country').code
        shipping_address['phone_number'] = tamara_txn_values.get(
            'billing_partner_phone')
        return shipping_address

    def _get_tamara_tax_amount(self, tamara_txn_values):
        tax_amount = dict()
        tax_cost = self.env['sale.order'].sudo().search(
            [('name', '=', tamara_txn_values.get('reference').split('-')[0])]).amount_tax
        tax_amount['amount'] = tax_cost
        tax_amount['currency'] = tamara_txn_values.get('currency').name
        return tax_amount

    def _get_tamara_total_amount(self, tamara_txn_values):
        total_amount = dict()
        total_amount['amount'] = tamara_txn_values.get('amount')
        total_amount['currency'] = tamara_txn_values.get('currency').name
        return total_amount

    def _get_tamara_shipping_amount(self, tamara_txn_values):
        shipping_amount = dict()
        sale_order = self.env['sale.order'].sudo().search(
            [('name', '=', tamara_txn_values.get('reference').split('-')[0])])
        shipping_cost = sale_order.amount_delivery if hasattr(sale_order,'amount_delivery') else 0.0
        shipping_amount['amount'] = shipping_cost
        shipping_amount['currency'] = tamara_txn_values.get('currency').name
        return shipping_amount

    def _get_tamara_mechant_url(self, tamara_txn_values):
        merchant_urls = dict()
        reference = tamara_txn_values.get('reference')
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        merchant_urls['success'] = str(urls.url_join(
            base_url, PaymentTamaraController.success_url)) + "?reference={}".format(reference)
        merchant_urls['failure'] = str(urls.url_join(
            base_url, PaymentTamaraController.failure_url)) + "?reference={}".format(reference)
        merchant_urls['cancel'] = str(urls.url_join(
            base_url, PaymentTamaraController.cancel_url)) + "?reference={}".format(reference)
        merchant_urls['notification'] = str(urls.url_join(
            base_url, PaymentTamaraController.notification_url)) + "?reference={}".format(reference)
        return merchant_urls
    # line.product_id.hs_code or
    def _get_tamara_items_detail(self, tamara_txn_values):
        items_data = []
        order = self.env['sale.order'].sudo().search(
            [('name', '=', tamara_txn_values.get('reference').split('-')[0])])
        for line in order.order_line:
            hs_code = line.product_id.hs_code if hasattr(line.product_id,'hs_code') else 'HS-123'
            defualt_code = line.product_id.default_code if hasattr(line.product_id,"default_code") else ''
            sku_code = (line.product_id.default_code if line.product_id.type == 'service' else line.product_id.default_code) or hs_code
            line_item = dict()
            line_item['reference_id'] = (order.name or '') + \
                                        (line.product_id.name or '') + (defualt_code or '')

            line_item['type'] = line.product_id.categ_id.name
            line_item['name'] = line.product_id.name
            line_item['sku'] =  sku_code
            line_item['quantity'] = int(line.product_uom_qty)
            line_item['total_amount'] = {
                'amount': line.price_total,
                'currency':  tamara_txn_values.get('currency').name,
            }
            items_data.append(line_item)
        return items_data

    def _tamara_make_data(self, tamara_txn_values):
        data = dict()
        context_dict = dict(self._context)
        data['order_reference_id'] = tamara_txn_values.get('reference')
        data['total_amount'] = self._get_tamara_total_amount(tamara_txn_values)
        data['description'] = tamara_txn_values.get('reference')
        data['country_code'] = tamara_txn_values.get(
            'partner_country').code
        data['payment_type'] = "PAY_BY_LATER"
        data['locale'] = context_dict.get('lang')
        data['items'] = self._get_tamara_items_detail(tamara_txn_values)
        data['consumer'] = self._get_tamara_consumer_data(tamara_txn_values)
        data['shipping_address'] = self._get_tamara_shipping_address(
            tamara_txn_values)
        data['tax_amount'] = self._get_tamara_tax_amount(tamara_txn_values)
        data['shipping_amount'] = self._get_tamara_shipping_amount(
            tamara_txn_values)
        data['merchant_url'] = self._get_tamara_mechant_url(tamara_txn_values)
        return data

    def get_payment_type(self,headers,api_end,path,country_code=None):
        api_end = api_end+path
        payment_type = '/payment-types'
        response = requests.get(url=api_end+payment_type,headers=headers,data=json.dumps({"country":country_code}))
        
        if response.status_code != 200:
            raise UserError(json.loads(response.content).get('message'))
        result = json.loads(response.content)[0].get('name',False)
        return result

    def _tamara_send_request(self, request_data, method=None, path=None):
        HEADERS = {
            'Authorization': 'Bearer ' + self.tamara_merchant_token,
            'Content-Type': 'application/json',
        }
        api_end = self.APIEND.get(
            "test_url") if self.state == 'test' else self.APIEND.get("live_url")

        try:
            payment_type = self.get_payment_type(HEADERS,api_end,path,request_data.get('country_code')) if request_data and request_data.get('country_code') else ''
            if payment_type:
                request_data.update({'payment_type':payment_type})

            if method == "post":
                # _logger.info(
                #     "######## API END ##########%s", api_end+path)
                # _logger.info(pprint.pprint(request_data))
                # _logger.info(
                #     "######## POST REQUEST DATA ##########%s", json.dumps(request_data))
                response = requests.post(
                    url=api_end+path, headers=HEADERS, data=json.dumps(request_data))
                # _logger.info(
                #     "########POST RESPONSE DATA##########%s", response.text)
                return response
            elif method == "get":
                # _logger.info("########GET REQUEST DATA##########")
                response = requests.get(url=api_end+path, headers=HEADERS)
                # _logger.info(
                #     "########GET RESPONSE DATA##########%s", response.text)
                return response
        except Exception as e:
            _logger.warning(
                "#WKDEBUG---TAMARA----Exception-----%r---------" % (e))
            raise UserError(e)

    def _tamara_verify_data(self, response):
        success = True
        data = dict()
        if response.status_code in range(200, 300):
            success = True
            data['success'] = success
            data['data'] = json.loads(response.text)
        else:
            success = False
            json_data = json.loads(response.text)
            data['success'] = success
            data['message'] = json_data.get('message')
            errors = []
            for error in json_data.get('errors'):
                if error.get("error_code"):
                    errors.append(error.get("error_code"))
            data['errors'] = errors
        return data

    def _tamara_make_request(self, request_data, method=None, path=None):
        response = self._tamara_send_request(
            request_data, method=method, path=path)
        resp_data = self._tamara_verify_data(response)
        if resp_data.get('success') == False:
            errors = ''
            for error in resp_data.get('errors'):
                errors += error+', '
                _logger.error("WK---Tamara-Err-Resp------%s", error)
            raise UserError(f"{resp_data.get('errors')} -> {errors}")
        return resp_data


    def _get_tamara_txn_url(self, tamara_txn_values):

        request_data = self._tamara_make_data(tamara_txn_values)
        resp_data = self._tamara_make_request(
            request_data, method="post", path="/checkout")
        return resp_data.get('data')

    def tamara_form_generate_values(self, values):
        tamara_txn_values = dict(values)
        self.tamara_reference_id = tamara_txn_values.get('reference')
        response_data = self._get_tamara_txn_url(tamara_txn_values)
        self.tamara_order_id = response_data.get('order_id')
        tamara_txn_values['tamara_order_id'] = self.tamara_order_id
        tamara_txn_values['tamara_checkout_id'] = response_data.get(
            'checkout_id')
        tamara_txn_values['tamara_checkout_url'] = response_data.get(
            'checkout_url')
        return tamara_txn_values


class PaymentTransactionTamara(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _tamara_form_get_tx_from_data(self, data):
        reference, orderId, paymentStatus = data.get(
            'reference'), data.get('orderId'), data.get('paymentStatus')
        if not reference or not paymentStatus:
            error_msg = _('Tamara: received data with missing reference (%s) or paymentStatus (%s)') % (
                reference, paymentStatus)
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = _(
                'Tamara: received data for reference %s') % (reference)
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return tx

    def _tamara_form_get_invalid_parameters(self, data):
        reference, orderId, paymentStatus = data.get(
            'reference'), data.get('orderId'), data.get('paymentStatus')
        if paymentStatus == "canceled":
            return
        invalid_parameters = []
        req_path = "/orders/" + str(orderId)
        order_details = self.acquirer_id._tamara_make_request(
            False, method="get", path=req_path)
        data = order_details.get('data')
        total_amount = data.get('total_amount').get('amount')
        currency = data.get('total_amount').get('currency')
        if float_compare(float(total_amount), self.amount, 2) != 0:
            invalid_parameters.append(
                ('Amount', total_amount, '%.2f' % self.amount))
        if currency != self.currency_id.name:
            invalid_parameters.append(
                ('Currency', currency, self.currency_id.name))
        if reference != self.reference:
            invalid_parameters.append(
                ('Reference', reference, self.reference))
        return invalid_parameters

    def _tamara_form_validate(self, data):
        reference, orderId, paymentStatus = data.get(
            'reference'), data.get('orderId'), data.get('paymentStatus')
        if self.state == 'done':
            _logger.warning(
                'Tamara: trying to validate an already validated tx (ref %s)' % self.reference)
            return True

        if paymentStatus == "approved":
            request_data = dict()
            request_data['orderId'] = orderId
            req_path = "/orders/{}/authorise".format(orderId)
            auth_response = self.acquirer_id._tamara_send_request(
                request_data, method="post", path=req_path)
            resp_data = self.acquirer_id._tamara_verify_data(auth_response)
            if resp_data.get('success') == False:
                self.write({
                    'acquirer_reference': orderId,
                    'state_message': resp_data.get('message'),
                })
                self._set_transaction_pending()
                return True
            else:
                auth_json_data = resp_data.get('data')
                auth_status = auth_json_data.get('status')
                if auth_status == "authorised":
                    self.write({'acquirer_reference': orderId})
                    self._set_transaction_authorized()
                    return True
                else:
                    self.write({'acquirer_reference': orderId})
                    self._set_transaction_pending()
                    return True

        elif paymentStatus == "canceled":
            cancel_msg = "Tamara: Transaction cancelled by customer"
            self.write({
                'acquirer_reference': orderId,
                'state_message': cancel_msg,
            })
            self._set_transaction_cancel()
            return True

        elif paymentStatus == "declined":
            error_msg = "Transaction Declined"
            self.write({
                'acquirer_reference': orderId,
                'state_message': error_msg,
            })
            self._set_transaction_error(msg=error_msg)
            return True

        else:
            error_msg = "Tamara: Received unknown status for Tamara reference %s, set as error:  %s" % (
                self.reference, paymentStatus)
            _logger.info(error_msg)
            self.write({
                'acquirer_reference': orderId,
                'state_message': error_msg,
            })
            self._set_transaction_error(msg=error_msg)
            return False
        
    def _process_notification_data_custom(self, data):
        reference, orderId, paymentStatus = data.get(
            'reference'), data.get('orderId'), data.get('paymentStatus')
        if self.state == 'done':
            _logger.warning(
                'Tamara: trying to validate an already validated tx (ref %s)' % self.reference)
            return True

        if paymentStatus == "approved":
            request_data = dict()
            request_data['orderId'] = orderId
            req_path = "/orders/{}/authorise".format(orderId)
            auth_response = self.acquirer_id._tamara_send_request(
                request_data, method="post", path=req_path)
            resp_data = self.acquirer_id._tamara_verify_data(auth_response)
            if resp_data.get('success') == False:
                self.write({
                    'acquirer_reference': orderId,
                    'state_message': resp_data.get('message'),
                })
                self._set_transaction_pending()
                return True
            else:
                auth_json_data = resp_data.get('data')
                auth_status = auth_json_data.get('status')
                if auth_status == "authorised":
                    self.write({'acquirer_reference': orderId})
                    self._set_transaction_authorized()
                    return True
                else:
                    self.write({'acquirer_reference': orderId})
                    self._set_transaction_pending()
                    return True

        elif paymentStatus == "canceled":
            cancel_msg = "Tamara: Transaction cancelled by customer"
            self.write({
                'acquirer_reference': orderId,
                'state_message': cancel_msg,
            })
            self._set_transaction_cancel()
            return True

        elif paymentStatus == "declined":
            error_msg = "Transaction Declined"
            self.write({
                'acquirer_reference': orderId,
                'state_message': error_msg,
            })
            self._set_transaction_error(msg=error_msg)
            return True

        else:
            error_msg = "Tamara: Received unknown status for Tamara reference %s, set as error:  %s" % (
                self.reference, paymentStatus)
            _logger.info(error_msg)
            self.write({
                'acquirer_reference': orderId,
                'state_message': error_msg,
            })
            self._set_transaction_error(msg=error_msg)
            return False

    def tamara_s2s_capture_transaction(self):
        self.ensure_one()
        request_data = dict()
        request_data['order_id'] = self.acquirer_reference
        request_data['total_amount'] = {
            'amount': self.amount,
            'currency': self.currency_id.name,
        }
        request_data['shipping_info'] = {
            'shipped_at': datetime.now().strftime("%Y-%m-%dT%H:%M:%Sz"),
            'shipping_company': "Delivery Carrier",
        }
        req_path = "/payments/capture"
        capture_response = self.acquirer_id._tamara_make_request(
            request_data, method="post", path=req_path)
        capture_json_data = capture_response.get('data')
        if capture_json_data.get('capture_id'):
            capture_msg = "Tamara: Transaction has been captured with capture id {}".format(
                capture_json_data.get('capture_id'))
            self.write({
                'state_message': capture_msg,
            })
            self._set_transaction_done()

    def tamara_s2s_void_transaction(self):
        self.ensure_one()
        request_data = dict()
        request_data['total_amount'] = {
            'amount': self.amount,
            'currency': self.currency_id.name,
        }
        req_path = "/orders/{}/cancel".format(self.acquirer_reference)
        cancel_response = self.acquirer_id._tamara_make_request(
            request_data, method="post", path=req_path)
        cancel_json_data = cancel_response.get('data')
        if cancel_json_data.get('cancel_id'):
            cancel_msg = "Tamara: Transaction cancelled with cancelled id {}".format(
                cancel_json_data.get('cancel_id'))
            self.write({
                'state_message': cancel_msg,
            })
            self._set_transaction_cancel()
