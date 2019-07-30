from odoo import api, fields, models
import sys
from datetime import datetime, timedelta
import math
from datetime import datetime, timedelta, time


def float_to_time(float_hour):
    return time(int(math.modf(float_hour)[1]), int(60 * math.modf(float_hour)[0]), 0)


def convert_to_float(time):
    hour = int(time[10:13])
    mins = float(time[14:16])
    float_min = mins / 60
    return hour + float_min - math.floor(float_min)

class AttendanceWizard(models.TransientModel):
    _name = 'attendance.calc.wizard'


    @api.multi
    def calculate_attendance(self):
        hr_employee_list = self.env['hr.employee'].search([])

        yesterday = (datetime.now().date() - timedelta(days=1)).strftime("%Y-%m-%d")
        for employee in hr_employee_list:
            check_in = False
            attendance_log = self.env['attendance.log'].search([('employee_id', '=', employee.id),
                                                                ('date', '<=', yesterday), ('is_calculated', '=', False)
                                                                   , ('status', '=', '0')])
            for log in attendance_log:
                if check_in == False:
                    self.env['hr.attendance'].create({
                        'employee_id': log.employee_id.id,
                        'check_in': log.punching_time,
                        'date': log.date
                    })
                    check_in = True
                log.is_calculated = True

        for employee in hr_employee_list:
            check_out = False
            attendance_log = self.env['attendance.log'].search([('employee_id', '=', employee.id),
                                                                ('date', '<=', yesterday), ('is_calculated', '=', False)
                                                                   , ('status', '=', '1')], order="punching_time desc")
            for log in attendance_log:
                if check_out == False:
                    hr_attendence_check = self.env['hr.attendance'].search([('date', '=', log.date),
                                                                            ('employee_id', '=', log.employee_id.id)])
                    if hr_attendence_check:
                        if hr_attendence_check.check_in > log.punching_time:
                            pass
                        else:
                            if hr_attendence_check:
                                hr_attendence_check.write({
                                    'check_out': log.punching_time
                                })
                            check_out = True
                log.is_calculated = True
