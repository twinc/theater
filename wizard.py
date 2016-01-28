# -*- coding: utf-8 -*-

from openerp import models, fields, api

class Wizard(models.TransientModel):
    _name = 'theater.wizard'
    
    def _default_time(self):
        return self.env['theater.time'].browse(self._context.get('active_id'))

    time_id = fields.Many2one('theater.time',
        string="Time", required=True, default=_default_time)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    
    @api.multi
    def subscribe(self):
        for time in self.time_id:
            time.attendee_ids |= self.attendee_ids
        return {}