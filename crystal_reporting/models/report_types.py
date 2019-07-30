from odoo import fields, models, api


class ReportTypes(models.Model):
    _name = 'report.types'

    name = fields.Char('Report Name')
