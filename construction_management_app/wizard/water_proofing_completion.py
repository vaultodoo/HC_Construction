from odoo import api, models, fields


class WaterProofCompletion(models.TransientModel):
    _name = 'water.proof.completion'

    date = fields.Date(default=fields.Date.context_today)
    attention = fields.Text(string="Attention")
    letter_body = fields.Html(string="Body of the letter")
    project_id = fields.Many2one('project.project', default=lambda self: self._context.get('active_id',False))
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def print_report(self):
        return self.env.ref('construction_management_app.action_water_proofing_completion_report').report_action(self)