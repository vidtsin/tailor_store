from odoo import fields, models, api
from odoo.exceptions import UserError, Warning


class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    is_hr_manager = fields.Boolean(string="HR Manager", default=False)

class CrystalReporting(models.Model):
    _name = 'crystal.reporting'
    _rec_name = 'employee_id'

    @api.model
    def get_hr_emails(self):
        emails = ','.join(e.work_email for e in self.env['hr.employee'].search([('is_hr_manager', '=', True)]))
        return emails

    employee_id = fields.Many2one('hr.employee', string="Employee")
    doc_type = fields.Many2one('report.types', string="Document Type")
    reason = fields.Text('Reason')
    body = fields.Html('Body')
    state = fields.Selection([('draft', 'Draft'),
                              ('sent', 'Sent'),
                              ('confirm', 'Confirm'),
                              ('approve', 'Approve'),
                              ('reject', 'Reject')], string="State", default='draft')
    number_of_prints = fields.Integer(default=0)
    url = fields.Char('URL')
    hr_managers_list = fields.Char(string='HR Managers', default=get_hr_emails)

    # Once the employee has created the record, employee has to request it from the Human resources. Therefore it is
    # passed to the sent stage. This below function is triggered when Request button is clicked and the state changes
    # from draft to sent
    @api.multi
    def request_doc(self):
        self.write({
            'state': 'sent'
        })

    # Once the employee has sent the request to HR, HR officer has confirm it. In this stage HR officer has to type the
    # body of the letter and send. This below function is triggered when Confirm button is clicked and the state changes
    # from sent to confirm and also a mail is triggered too.
    @api.multi
    def confirm_doc(self):
        if self.body == '<p><br></p>':
            raise UserError('You cannot leave Body empty')
        self.write({
            'state': 'confirm'
        })

        template_id = self.env.ref('crystal_reporting.email_to_approve_request')
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url = base_url + '/web?login/#id=' + str(
            self.id) + '&view_type=form&model=crystal.reporting'
        self.write({
            'url': url,
        })
        self.env['mail.template'].browse(template_id.id).send_mail(self.id, True)

    # Once the officer has confirmed the request, HR Manager has the option either to approve or reject it.
    # This below function is triggered when Approve button is clicked and the state changes from confirm to approve
    @api.multi
    def approve_doc(self):
        self.write({
            'state': 'approve'
        })

    # Once the officer has confirmed the request, HR Manager has the option either to approve or reject it.
    # This below function is triggered when Reject button is clicked and the state changes from confirm to reject
    @api.multi
    def reject_doc(self):
        self.write({
            'state': 'reject'
        })

    # Once the HR Manager has approved the request, HR Manager has the option to download requested letter.
    # This below function is triggered when Print Document button is clicked. First time the original document is
    # printed and then after the copy
    @api.multi
    def print_doc(self):
        self.write({
            'number_of_prints': self.number_of_prints + 1
        })
        return self.env.ref('crystal_reporting.action_crystal_report').report_action(self)




