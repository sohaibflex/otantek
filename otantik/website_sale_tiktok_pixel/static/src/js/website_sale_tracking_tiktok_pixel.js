odoo.define('website_sale_tiktok_pixel.tracking', function (require) {
"use strict";

var websiteSaleTrackingAlternative = require('website_sale_tracking_base.tracking');

websiteSaleTrackingAlternative.include({

    trackingSendEventData: function(eventType, eventData) {
        if (eventData['tiktok_pixel'] !== undefined && Array.isArray(eventData['tiktok_pixel'])) {
            const websiteTikTok = window.ttq || function () {};
            for(var i = 0; i < eventData['tiktok_pixel'].length; i++) {
                if (this.trackingIsLogged()) { console.log(eventData['tiktok_pixel'][i]); }
                var tracking_id = eventData['tiktok_pixel'][i]['key'];
                var run_script = eventData['tiktok_pixel'][i]['run_script'];
                var event_name = eventData['tiktok_pixel'][i]['event_name'];
                var event_data = eventData['tiktok_pixel'][i]['data'];
                var user_data = eventData['tiktok_pixel'][i]['user_data'];
                if (event_data !== undefined && run_script !== undefined && run_script) {
                    if (user_data) {
                        websiteTikTok.identify(user_data);
                    }
                    websiteTikTok.instance(tracking_id).track(event_name, event_data);
                }
            }
        }
        return this._super.apply(this, arguments);
    },
});
});
