

from odoo import models, fields, api, _,tools
from datetime import datetime, timedelta

class ManuallyLoyalty(models.TransientModel):
	_name = 'loyalty.wizard.manually'
	_description = "Manual Loyalty Wizard "


	partner_ids = fields.Many2many('res.partner','m2m_pi_ml','pi_id','ml_id',string='Customer Name')
	loyalty_points = fields.Float(string='Loyalty Points')

	def button_submit(self):
		if self.partner_ids:
			for partner in self.partner_ids:
				vals = {
					'partner_id':partner.id,
					'points':self.loyalty_points,
					'state' : 'done',
					'transaction_type' : 'credit'
				}
				self.env['all.loyalty.history'].create(vals)
			context = {'default_name':'Record Imported Successfully'} 
			return {
				'name': 'Success',
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'custom.pop.message',
				'target':'new',
				'context':context
			}

