# -*- coding: utf-8 -*-
from openerp import fields, models

class Partner(models.Model):
    _inherit = 'res.partner'

    # Add a new column to the res.partner model, by default partners are not
    # Company
    company = fields.Boolean("Company", default=False)

    time_ids = fields.Many2many('theater.time',
        string="Attended Times", readonly=True)