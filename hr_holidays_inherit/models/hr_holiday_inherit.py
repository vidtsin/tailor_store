from odoo import fields, models, api, _
from odoo.exceptions import UserError, Warning, ValidationError

class EmployeeInherit(models.Model):
    _inherit = 'hr.leave'

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate2', 'Third Approval'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a leave request is created." +
             "\nThe status is 'To Approve', when leave request is confirmed by user." +
             "\nThe status is 'Refused', when leave request is refused by manager." +
             "\nThe status is 'Approved', when leave request is approved by manager.")
    third_approver_id = fields.Many2one(
        'hr.employee', string='Third Approval', readonly=True, copy=False,
        help='This area is automaticly filled by the user who validate the leave with second level (If Leave type need second validation)')

    @api.multi
    def action_validate(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if any(holiday.state not in ['confirm', 'validate1', 'validate2'] for holiday in self):
            raise UserError(_('Leave request must be confirmed in order to approve it.'))

        if not self.state == 'validate1':
            self.write({'state': 'validate'})
        else:
            self.write({'state': 'validate2'})

        self.filtered(lambda holiday: holiday.validation_type == 'both').write(
            {'second_approver_id': current_employee.id})
        self.filtered(lambda holiday: holiday.validation_type == 'both').write(
            {'third_approver_id': current_employee.id})
        self.filtered(lambda holiday: holiday.validation_type != 'both').write(
            {'first_approver_id': current_employee.id})

        for holiday in self.filtered(lambda holiday: holiday.holiday_type != 'employee'):
            if holiday.holiday_type == 'category':
                employees = holiday.category_id.employee_ids
            elif holiday.holiday_type == 'company':
                employees = self.env['hr.employee'].search([('company_id', '=', holiday.mode_company_id.id)])
            else:
                employees = holiday.department_id.member_ids

            if self.env['hr.leave'].search_count(
                    [('date_from', '<=', holiday.date_to), ('date_to', '>', holiday.date_from),
                     ('state', 'not in', ['cancel', 'refuse']), ('holiday_type', '=', 'employee'),
                     ('employee_id', 'in', employees.ids)]):
                raise ValidationError(_('You can not have 2 leaves that overlaps on the same day.'))

            values = [holiday._prepare_holiday_values(employee) for employee in employees]
            leaves = self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True,
            ).create(values)
            leaves.action_approve()
            # FIXME RLi: This does not make sense, only the parent should be in validation_type both
            if leaves and leaves[0].validation_type == 'both':
                leaves.action_validate()

    @api.multi
    def action_refuse(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1', 'validate2']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            if holiday.state == 'validate1':
                holiday.write({'state': 'refuse', 'first_approver_id': current_employee.id})
            elif holiday.state == 'validate2':
                holiday.write({'state': 'refuse', 'third_approver_id': current_employee.id})
            else:
                holiday.write({'state': 'refuse', 'second_approver_id': current_employee.id})
            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self._remove_resource_leave()
        self.activity_update()
        return True







