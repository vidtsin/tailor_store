from odoo import fields, models, api
from odoo.exceptions import UserError, Warning


class EmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    # is_hr_manager = fields.Boolean(string="HR Manager", default=False)

class HrWarningLetters(models.Model):
    _name = 'hr.warning.letters'
    _rec_name = 'employee_id'

    @api.model
    def get_hr_emails(self):
        emails = ','.join(e.work_email for e in self.env['hr.employee'].search([('is_hr_manager', '=', True)]))
        return emails

    employee_id = fields.Many2one('hr.employee', string="Employee")
    warning1_reason = fields.Text('Reason')
    warning2_reason = fields.Text('Reason')
    warning1_body = fields.Html('Body')
    warning2_body = fields.Html('Body')
    state = fields.Selection([('draft', 'Draft'),
                              ('level_1_warning', 'Level 1 Warning'),
                              ('level_1_warning_issue', 'Level 1 Warning Issued'),
                              ('level_2_warning', 'Level 2 Warning'),
                              ('level_2_warning_issue', 'Level 2 Warning Issued')], string="State", default='draft')
    url = fields.Char('URL')
    hr_managers_list = fields.Char(string='HR Managers', default=get_hr_emails)

    # HR officer creates and raises the first warning for an employee, and add the body of letter, and then send it to
    # HR manager. Automated email is triggered and sent to HR Manager. This function is triggered when Raise First
    # Warning button is clicked
    @api.multi
    def raise_first_warning(self):
        if self.warning1_body == '<p><br></p>':
            raise UserError('You cannot leave Body empty')
        self.write({
            'state': 'level_1_warning'
        })

        template_id = self.env.ref('hr_warning_letters.email_to_raise_first_warning')
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url = base_url + '/web?login/#id=' + str(
            self.id) + '&view_type=form&model=hr.warning.letters'
        self.write({
            'url': url,
        })
        self.env['mail.template'].browse(template_id.id).send_mail(self.id, True)

    # Once HR Manager has informed that a Warning has Raise , HR Manager can generate warning letter for the employee
    # This function is triggered when Generate First Warning button is clicked
    @api.multi
    def generate_warning_1(self):
        self.write({
            'state': 'level_1_warning_issue'
        })
        return self.env.ref('hr_warning_letters.action_first_warning_report').report_action(self)

    # HR officer creates and raises the Second warning for an employee, and add the body of letter, and then send it to
    # HR manager. Automated email is triggered and sent to HR Manager. This function is triggered when Raise Second
    # Warning button is clicked
    @api.multi
    def raise_second_warning(self):
        if self.warning2_body == '<p><br></p>':
            raise UserError('You cannot leave Body empty')
        self.write({
            'state': 'level_2_warning'
        })

        template_id = self.env.ref('hr_warning_letters.email_to_raise_second_warning')
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url = base_url + '/web?login/#id=' + str(
            self.id) + '&view_type=form&model=hr.warning.letters'
        self.write({
            'url': url,
        })
        self.env['mail.template'].browse(template_id.id).send_mail(self.id, True)

    # Once HR Manager has informed that a Warning has Raise , HR Manager can generate warning letter for the employee
    # This function is triggered when Generate Second Warning button is clicked
    @api.multi
    def generate_warning_2(self):
        self.write({
            'state': 'level_2_warning_issue'
        })
        return self.env.ref('hr_warning_letters.action_second_warning_report').report_action(self)




