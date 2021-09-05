from odoo import api, models, fields


class MaterialSupplyConfirmation(models.TransientModel):
    _name = 'material.supply.confirmation'

    date = fields.Date(default=fields.Date.context_today)
    to_address = fields.Text(string="To")
    client = fields.Text(string="Client/Owner")
    consultant = fields.Text(string="Consultant")
    nature_work = fields.Html(string="Letter Body")
    project_id = fields.Many2one('project.project', default=lambda self: self._context.get('active_id',False))
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def print_report(self):
        return self.env.ref('construction_management_app.action_material_supply_confirmation_report').report_action(self)