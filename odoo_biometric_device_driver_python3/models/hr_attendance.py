from odoo import models, fields, api, exceptions, _
import math
from datetime import datetime, time, timedelta
from time import mktime


def float_to_time(float_hour):
    return time(int(math.modf(float_hour)[1]), int(60 * math.modf(float_hour)[0]), 0)


def convert_to_float(time):
    hour = int(time[10:13])
    mins = float(time[14:16])
    float_min = mins / 60
    return hour + float_min - math.floor(float_min)


def convert_date_to_float(date_obj):
    obj = datetime.datetime.strptime(str(date_obj), '%H:%M:%S')
    float_value = float(0.00)

    float_value += float(obj.hour) * 3600
    float_value += float(obj.minute) * 60
    float_value += float(obj.second)
    return float(float_value)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    date = fields.Date('Date')
    in_time = fields.Float('In Time', compute='_get_in_time', readonly=True)
    out_time = fields.Float('Out Time', compute='_get_out_time', readonly=True)


    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                pass
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    pass

    @api.one
    @api.depends('check_in')
    def _get_in_time(self):
        if self.check_in:
            check_in = fields.Datetime.to_string(fields.Datetime.from_string(self.check_in) + timedelta(hours=5, minutes=30))
            self.in_time = convert_to_float(check_in)


    @api.one
    @api.depends('check_out')
    def _get_out_time(self):
        if self.check_out:
            check_out = fields.Datetime.to_string(fields.Datetime.from_string(self.check_out) + timedelta(hours=5, minutes=30))
            self.out_time = convert_to_float(check_out)

    @api.one
    @api.depends('check_in', 'check_out')
    def _get_working_time(self):
        if self.check_in and self.check_out:
            if self.check_out > self.check_in:
                check_in = fields.Datetime.to_string(
                    fields.Datetime.from_string(self.check_in) + timedelta(hours=5, minutes=30))
                check_out = fields.Datetime.to_string(fields.Datetime.from_string(self.check_out) + timedelta(hours=5, minutes=30))
                self.working_time = convert_to_float(check_out) - convert_to_float(check_in)




