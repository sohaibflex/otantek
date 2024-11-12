odoo.define('website_sale_tracking_base.website_tracking', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');
    const websiteSaleTrackingAlternative = require('website_sale_tracking_base.tracking');

    publicWidget.registry.websiteTrackingAlternative = websiteSaleTrackingAlternative.extend({
        selector: '#oe_structure_website_form_contact_us_thanks_1',

        start: function (ev) {
            this.trigger_up('tracking_lead');
            return this._super.apply(this, arguments);
        },
    });
    return publicWidget.registry.websiteTrackingAlternative;
});



