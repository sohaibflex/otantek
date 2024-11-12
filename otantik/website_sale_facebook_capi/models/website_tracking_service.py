# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

import json
import logging
import requests

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request
from .website_tracking_log import WebsiteTrackingLog

_logger = logging.getLogger(__name__)


class WebsiteTrackingService(models.Model):
    _inherit = "website.tracking.service"

    fb_capi_is_active = fields.Boolean(string='Conversions API Mode')
    fb_capi_test_event_code = fields.Char(
        string='Test Event Code',
        help='If you activate this option, the CAPI will work in Test Mode. '
             'Use this code to test your server events in the Test Events feature '
             'in Events Manager.',
    )
    fb_capi_access_token = fields.Text(string='Access Token')

    @api.constrains('type', 'is_internal_logged', 'fb_capi_is_active')
    def _check_fb_capi_is_internal_logged(self):
        for service in self:
            # flake8: noqa: E501
            if service.type == 'fbp' and service.fb_capi_is_active and not service.is_internal_logged:
                raise ValidationError(_("You have to activate internal logging for Facebook CAPI services."))

    def is_fb_capi(self):
        self.ensure_one()
        return self.type == 'fbp' and self.fb_capi_is_active

    def extra_log_data(self):
        self.ensure_one()
        res = super(WebsiteTrackingService, self).extra_log_data()
        if self.is_fb_capi():
            res.update({
                'channel': 'fb_capi',
                'state': 'to_send',
                'fbp': request and request.httprequest.cookies.get('_fbp', ''),
                'fbc': request and request.httprequest.cookies.get('_fbc', ''),
            })
        return res

    def fb_capi_send_request(self, logs: WebsiteTrackingLog):
        self.ensure_one()
        service = self
        response = None

        request_data = {'data': logs.fb_capi_get_event_data()}
        if not request_data['data']:
            return response

        if service.fb_capi_test_event_code:
            request_data.update({'test_event_code': service.fb_capi_test_event_code})

        log_vals = {'api_sent_date': fields.Datetime.now()}
        try:
            response = requests.post(
                url=f'https://graph.facebook.com/v16.0/{service.key}/events',
                json=request_data,
                params={'access_token': service.fb_capi_access_token}
            )

            if service.website_id.tracking_is_logged:
                _logger.debug("[FB CAPI] Response: %s | %s | %s" % (
                    response.status_code,
                    response.json(),
                    response.text,
                ))
            response.raise_for_status()
            log_vals.update({'state': 'sent'})

        except requests.HTTPError as e:
            _logger.error(
                "[FB CAPI] HTTP Error: %r, msg: %r, content: %r)",
                e.response.status_code, e.response.reason, response.json(),
            )
            log_vals.update({
                'state': 'error',
                'api_response': "%s | Reason: %s | %s" % (
                    e.response.status_code, e.response.reason, json.dumps(response.json())
                ),
                # response.text.decode(response.encoding)
            })
        except Exception as e:
            _logger.error("[FB CAPI] Other Error: %s" % str(e))
            log_vals.update({
                'state': 'error',
                'api_response': str(e),
            })
        else:
            if response.status_code != requests.codes.ok:
                _logger.error(
                    "[FB CAPI] Request Error: %r, msg: %r, content: %r)",
                    response.status_code, response.reason, response.json(),
                )
                log_vals.update({
                    'state': 'error',
                    'api_response': "%s | %s" % (response.status_code, json.dumps(response.json())),
                })

        finally:
            logs.sudo().write(log_vals)

        return response

    @api.model
    def _fb_capi_send_events(self):
        """Method to make batch request by the cron."""
        services = self.search([
            ('type', '=', 'fbp'),
            ('fb_capi_is_active', '=', True),
        ])
        for service in services:
            logs = self.env['website.tracking.log'].search([
                ('service_id', '=', service.id),
                ('channel', '=', 'fb_capi'),
                ('state', '=', 'to_send'),
                # The "event_time" can be up to 7 days before you send an event to Meta
                ('create_date', '>', fields.Datetime.now() - timedelta(days=7)),
            ])
            service.fb_capi_send_request(logs)

    @api.model
    def _fields_to_invalidate_cache(self):
        res = super(WebsiteTrackingService, self)._fields_to_invalidate_cache()
        res += ['fb_capi_is_active']
        return res
