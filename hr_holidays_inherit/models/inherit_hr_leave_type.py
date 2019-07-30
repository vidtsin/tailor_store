from odoo import fields, api, models


class InheritHrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    request_unit = fields.Selection([
        ('day', 'Day')],
        default='day', string='Take Leaves in', required=True)