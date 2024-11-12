odoo.define('website_sale_facebook_pixel.tracking', function (require) {
"use strict";

var websiteSaleTrackingAlternative = require('website_sale_tracking_base.tracking');

websiteSaleTrackingAlternative.include({

    _trackingFacebookPixel: function () {
        const websiteFBP = window.fbq || function () {};
        if (this.trackingIsLogged()) {
            console.log('DO _trackingFacebookPixel');
        }
        websiteFBP.apply(this, arguments);
    },

    trackingSendEventData: function(eventType, eventData) {
        if (this.trackingIsLogged()) {
            console.log('-- RUN Facebook Pixel --');
        }
        if (eventData['fbp'] !== undefined && Array.isArray(eventData['fbp'])) {
            for(var i = 0; i < eventData['fbp'].length; i++) {
                if (this.trackingIsLogged()) {
                    console.log(eventData['fbp'][i]);
                }
                var run_script = eventData['fbp'][i]['run_script']
                var event_name = eventData['fbp'][i]['event_name']
                var tracking_id = eventData['fbp'][i]['key']
                var event_data = eventData['fbp'][i]['data']
                if (event_data !== undefined && run_script !== undefined && run_script) {
                    this._trackingFacebookPixel('trackSingle', tracking_id, event_name, event_data);
                }
            }
        }
        return this._super.apply(this, arguments);
    },
});
});
