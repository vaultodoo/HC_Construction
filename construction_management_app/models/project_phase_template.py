from odoo import api, models, fields


class ProjectPhaseTemplate(models.Model):
    _name = 'project.phase.template'
    _order = 'sequence'

    name = fields.Char(string="Stage Name")
    sequence = fields.Integer(string="Sequence")
    set_default = fields.Boolean(string="Default?")
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')

