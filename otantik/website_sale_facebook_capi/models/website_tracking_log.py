# Copyright © 2023 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

import json
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WebsiteTrackingLog(models.Model):
    _inherit = "website.tracking.log"

    channel = fields.Selection(
        selection_add=[('fb_capi', 'Facebook CAPI')],
        ondelete={'fb_capi': 'cascade'},
    )
    fbp = fields.Char(string="Facebook browser ID")
    fbc = fields.Char(string="Facebook click ID")

    def fbp_capi_get_user_data(self):
        self.ensure_one()
        log = self
        user_data = {}

        visitor = log.visitor_id.sudo()
        if visitor and log.service_id.track_id_external:
            user_data["external_id"] = visitor.access_token
        if log.service_id.track_ip_address:
            user_data["client_ip_address"] = log.user_ip_address or ''
        if log.service_id.track_user_agent:
            user_data["client_user_agent"] = log.user_agent or ''

        if visitor:
            country = visitor.partner_id.country_id or visitor.country_id
            if log.service_id.track_country and country:
                user_data["country"] = self._hash_sha256(country.name)

            if log.service_id.track_city and visitor.partner_id.city:
                user_data["ct"] = self._hash_sha256(visitor.partner_id.city)

            if log.service_id.track_email and visitor.email:
                user_data["em"] = [self._hash_email(visitor.email)]

            phone = visitor.partner_id and (
                visitor.partner_id.phone or visitor.partner_id.mobile) or visitor.mobile
            if log.service_id.track_phone and phone and country:
                user_data["ph"] = [
                    self._hash_phone_number(phone, country, remove_plus=True)]

        return user_data

    def fb_capi_get_event_data(self):
        datas = []
        for log in self:
            payload = json.loads(log.payload)
            payload_data = payload['data']
            data = {
                "event_name": payload.get('event_name'),
                "event_id": str(log.id),
                "event_time": self._to_unix_time(log.create_date),
                "action_source": "website",
                "event_source_url": log.url or '',
                "user_data": {},
                "custom_data": payload_data,
            }

            user_data = data['user_data']
            user_data["fbp"] = log.fbp or ''
            user_data["fbc"] = log.fbc or ''
            user_data.update(log.fbp_capi_get_user_data())

            datas.append(data)
            if log.website_id.tracking_is_logged:
                _logger.debug("[FB CAPI] Request Data: %s" % data)

        return datas

    def action_send_event(self):
        self.ensure_one()
        self.service_id.fb_capi_send_request(self)
        return super(WebsiteTrackingLog, self).action_send_event()

