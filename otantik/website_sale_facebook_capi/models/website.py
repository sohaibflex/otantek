from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _tracking_run_script(self, service, product_data, order, event_type):
        """Do not run the JS script method to a send data to FB,
        if the CAPI was activated."""
        self.ensure_one()
        if service.is_fb_capi():
            return False
        return super(Website, self)._tracking_run_script(service, product_data, order, event_type)

    def _fbp_allowed_services(self):
        services = super(Website, self)._fbp_allowed_services()
        return services.filtered(lambda s: not s.fb_capi_is_active)
