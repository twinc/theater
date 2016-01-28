# -*- coding: utf-8 -*-
from datetime import timedelta
from openerp import models, fields, api, exceptions

class Movie(models.Model):
    _name = 'theater.movie'

    name = fields.Char(string="Movie", required=True)
    description = fields.Text()
    
    type_id = fields.Many2one('res.users',
        ondelete='set null', string="Type", index=True)
    
    time_ids = fields.One2many('theater.time', 'movie_id', string="Times")
    
    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Movie, self).copy(default)
    
    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the movie should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The movie title must be unique"),
    ]
    
    
class Time(models.Model):
    _name = 'theater.time'

    theatername = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    active = fields.Boolean(default=True)
    color = fields.Integer()
    
    company_id = fields.Many2one('res.partner', string="Company",
        domain=['|', ('company', '=', True),
                     ('category_id.name', 'ilike', "Seller")])
    movie_id = fields.Many2one('theater.movie',
        ondelete='cascade', string="Movie", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    
    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    end_date = fields.Date(string="End Date", store=True,
        compute='_get_end_date', inverse='_set_end_date')
    
    hours = fields.Float(string="Duration in hours",
                         compute='_get_hours', inverse='_set_hours')
    
    attendees_count = fields.Integer(
        string="Attendees count", compute='_get_attendees_count', store=True)
    
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('done', "Done"),
    ], default='draft')

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_done(self):
        self.state = 'done'
    
    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats
                
    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': "Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                },
            }
            
    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            start = fields.Datetime.from_string(r.start_date)
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = start + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date - start_date).days + 1
    
    @api.depends('duration')
    def _get_hours(self):
        for r in self:
            r.hours = r.duration * 24

    def _set_hours(self):
        for r in self:
            r.duration = r.hours / 24
    
    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)
    
    @api.constrains('company_id', 'attendee_ids')
    def _check_company_not_in_attendees(self):
        for r in self:
            if r.company_id and r.company_id in r.attendee_ids:
                raise exceptions.ValidationError("A time's company can't be an attendee")
            