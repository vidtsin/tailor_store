from odoo import api, fields, models, _
import datetime
from datetime import timedelta


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    is_half_day = fields.Boolean('Half Day',  default=False)
    half_day_date = fields.Date('Date')

    # When selecting is a half day check box, change the to date and the from date according to the on_change event
    @api.onchange('is_half_day', 'half_day_date')
    def _set_half_days_times(self):
        if self.is_half_day:
            if self.half_day_date:
                date_from = self.half_day_date.strftime('%Y-%m-%d %H:%M:%S')
                self.date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S') - timedelta(hours=5,
                                                                                                        minutes=30,
                                                                                                        seconds=0)

                self.date_to = datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S') + timedelta(hours=6,
                                                                                                      minutes=30,
                                                                                                      seconds=0)
