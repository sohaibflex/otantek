# Copyright © 2020 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (support@garazd.biz)
# @author: Iryna Razumovska (support@garazd.biz)
# License OPL-1 (https://www.odoo.com/documentation/15.0/legal/licenses.html).

import logging

from odoo.http import request, content_disposition
from werkzeug.exceptions import Forbidden, NotFound

from odoo import _, http, models

_logger = logging.getLogger(__name__)


class ProductFeed(http.Controller):

    def _validate_feed_request(self, feed_id, feed_name, **kwargs):
        """Check a feed request.

        :param string feed_id: a feed id
        :return: http response or True if everything is ok
        """
        if not (feed_id or feed_name):
            return NotFound()
        try:
            if feed_id:
                domain = [('id', '=', int(feed_id))]
            else:
                domain = [('filename', '=', str(feed_name))]
            feed = request.env['product.data.feed'].search(domain, limit=1)
        except ValueError:
            return NotFound()
        if not feed:
            return NotFound()

        # Check website
        if feed.website_ids and request.website not in feed.website_ids:
            return NotFound()

        # Check token
        if feed.use_token:
            access_token = kwargs.get('access_token')
            if not access_token or feed.access_token != access_token:
                return Forbidden()

        return feed

    def _get_mimetype(self, file_type) -> str or None:
        """Determinate a mimetype for a feed.

        :param string file_type: a feed file_type value
        :return: string or None
        """
        mimetypes = {
            'csv': 'text/csv;charset=utf-8',
            'tsv': 'text/tab-separated-values;charset=utf-8',
            'xml': 'application/xml;charset=utf-8'
        }
        return mimetypes.get(file_type, None)

    @http.route([
        '/product_data/<model("product.data.feed"):feed_id>/feed.csv',
        '/product_data/<string:feed_name>.csv',
        '/product_data/<model("product.data.feed"):feed_id>/feed.xml',
        '/product_data/<string:feed_name>.xml',
    ],
        type='http',
        auth='public',
        website=True,
        multilang=False,
        sitemap=False,
    )
    def product_data_feed(self, feed_id=None, feed_name=None, **kwargs):
        """Controller to return CSV/TSV product data feed."""

        feed = self._validate_feed_request(feed_id, feed_name, **kwargs)
        if not isinstance(feed, models.BaseModel):
            return feed

        mimetype = self._get_mimetype(feed.file_type)
        if not mimetype:
            return NotFound()

        try:
            content = feed.sudo().generate_data_file()
        except Exception as e:
            msg = _("Error: %s") % str(e)
            _logger.error(msg)
            feed.message_post(body=_("<p class='text-danger'>%s</p>") % msg)
            return NotFound()

        headers = [('Content-Type', mimetype)]
        if feed.content_disposition == 'attachment':
            headers += [
                ('Content-Length', len(content)),
                ('Content-Disposition', content_disposition(feed._get_file_name())),
            ]
        return request.make_response(content, headers)
