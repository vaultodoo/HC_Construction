# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    type_of_construction = fields.Selection(
        [('agricultural', 'Agricultural'),
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('institutional','Institutional'),
        ('industrial','Industrial'),
        ('heavy_civil','Heavy civil'),
        ('environmental','Environmental'),
        ('other','other')],
        string='Types of Construction'
    )
    location_id = fields.Many2one(
        'res.partner',
        'Location'
    )
    notes_ids = fields.One2many(
        'note.note', 
        'project_id', 
        string='Notes',
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count', 
        string="Notes",
        store=True,
    )

    project_phase_ids = fields.Many2many('project.phase.template', string="Project Phases")
    stage_allocated = fields.Boolean()
    sales_person = fields.Many2one('res.users', string="Sales Person")
    job_order = fields.Char(string="Job Order")
    plot_no = fields.Char(string="Plot No")
    document_ids = fields.One2many('upload.documents', 'project_id', string="Documents")
    stage_id = fields.Many2one('project.phase.template', ondelete='restrict', tracking=True, index=True, copy=False,domain="[('id', 'in', project_phase_ids)]")
    project_task_ids = fields.One2many('project.task', 'project_id')

    @api.depends()
    def _compute_notes_count(self):
        for project in self:
            project.notes_count = len(project.notes_ids)

    # @api.multi #odoo13
    def view_notes(self):
        for rec in self:
            res = self.env.ref('construction_management_app.action_project_note_note')
            res = res.read()[0]
            res['domain'] = str([('project_id','in',rec.ids)])
        return res

    @api.model
    def create(self,vals):
        rtn = super(ProjectProject,self).create(vals)
        stage_obj = self.env['project.task.type']
        stage_ids = stage_obj.search([('set_default', '=', True)])

        project_ids = [x.id for x in rtn]
        for stage in stage_ids:
            stage.sudo().write({'project_ids': [(4,tuple(project_ids),0)]})

        return rtn

    def allocate_stage_phase(self):
        return {
            "name": _("Allocate Stage Phase"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "project.phase.wiz",
            "target": "new",
        }
    
    def generate_proforma_invoice(self):
        completed_phases = self.project_task_ids.filtered(lambda l: l.final_stage == True and l.proforma_generated != 'yes')
        return {
            "name": _("Pro-Forma Invoice"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "proforma.invoice",
            "target": "new",
            'context': {'default_sale_order_id': self.sale_order_id.id, 'default_project_id': self.id,
                        'default_sale_order_value': self.sale_order_id.amount_total, 'default_task_ids': completed_phases.ids,
                        'default_sale_name': self.sale_order_id.name, 'default_partner_id': self.partner_id.id}
        }


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    set_default = fields.Boolean('Default?')
    final_stage = fields.Boolean(string="Is Final Stage")

    @api.model
    def create(self, vals):
        if vals.get('final_stage'):
            stages = self.search([('final_stage', '=', vals['final_stage'])])
            if len(stages) > 0:
                raise ValidationError("You cannot assign final stage to multiple task stages")
        return super(ProjectTaskType, self).create(vals)

    def write(self, vals):
        if vals.get('final_stage'):
            stages = self.search([('final_stage', '=', vals['final_stage'])])
            if len(stages) > 0:
                raise ValidationError("You cannot assign final stage to multiple task stages")
        return super(ProjectTaskType, self).write(vals)


class ProjectPhases(models.TransientModel):
    _name = 'project.phase.wiz'

    project_phase_ids = fields.Many2many('project.phase.template', string="Project Phases")
    project_id = fields.Many2one('project.project', default=lambda self: self._context.get('active_id',False))

    def allocate(self):
        if self.project_phase_ids:
            self.project_id.project_phase_ids = [(4, i) for i in self.project_phase_ids.ids]
            self.project_id.stage_allocated = True
            search_domain = [('id', 'in', self.project_phase_ids.ids)]
            phase = self.env['project.phase.template']
            task_type = self.env['project.task.type'].search([], order= self.env['project.task.type']._order, limit=1)
            stage = phase.search(search_domain, order= phase._order, limit=1).id
            self.project_id.stage_id = stage
            for pro in self.project_phase_ids:
                tasks = self.env['project.task'].create({
                    'name': pro.name,
                    'project_id': self.project_id.id,
                    'phase_id': pro.id,
                    'stage_id': task_type.id
                })
                tasks.stage_id.project_ids = [(4, self.project_id.id)]


class UploadDocuments(models.Model):
    _name = 'upload.documents'

    file = fields.Binary(string="File")
    description = fields.Char(string="Description")
    project_id = fields.Many2one('project.project')
    phase_ids = fields.Many2many('project.phase.template', 'phase_document_rel', 'upload_documents_id', 'phase_id', compute='get_phases')
    project_phase_ids = fields.Many2many('project.phase.template', string="Project Phases")
    
    def get_phases(self):
        if self.project_id:
            self.phase_ids = [(4,i)for i in self.project_id.project_phase_ids.ids]

    


