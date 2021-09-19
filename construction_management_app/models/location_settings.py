from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LocationSettings(models.Model):
    _name = 'location.settings'

    name = fields.Char(cmpute='get_name', store=True)
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        copy=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=False,
        copy=True,
    )
    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False,tracking=True
    )

    @api.depends('location_id', 'dest_location_id')
    def get_name(self):
        for rec in self:
            rec.name = rec.location_id.name+"/"+rec.dest_location_id.name


    @api.model
    def create(self, vals_list):
        slf = self.env['location.settings'].search_count([])
        if slf == 1:
            raise ValidationError("You cannot add more than one location settings")
        return super(LocationSettings, self).create(vals_list)
