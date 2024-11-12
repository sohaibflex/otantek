from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[('submit_to_manager', 'Submit To Manager'),('manager_approval', 'Manager Approval')])

    hr_employee_id = fields.Many2one('hr.employee', string='Employee',compute='_compute_employee_id')

    #need to bring related employee id with current user

    @api.depends('hr_employee_id')
    def _compute_employee_id(self):
        for record in self:
            # Use sudo() to search hr.employee records with elevated permissions
            record.hr_employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)

    def action_submit_to_manager(self):
        for rec in self:
            user_email = rec.hr_employee_id.parent_id.work_email
            # Send email to manager with sudo privileges
            self.env['mail.mail'].sudo().create({
                'subject': 'Scrap Picking Approval',
                'body_html': 'Scrap Picking Request for Scrap Picking ID: %s' % rec.name,
                'email_to': user_email,
            }).send()
        self.write({'state': 'submit_to_manager'})

    def action_manager_approval(self):
        self.write({'state': 'manager_approval'})

    def find_employee(self):
        for record in self:
            # Call the compute method with sudo privileges
            record.sudo()._compute_employee_id()

