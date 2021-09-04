from odoo import api, models, fields


class SubContractAgreement(models.TransientModel):
    _name = 'sub.contract.agreement'

    date = fields.Date(default=fields.Date.context_today)
    client = fields.Text(string="Client/Owner")
    consultant = fields.Text(string="Consultant")
    contact = fields.Text(string="Contact")
    nature_work = fields.Html(string="Nature of work")
    project_id = fields.Many2one('project.project', default=lambda self: self._context.get('active_id',False))
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def print_report(self):
        return self.env.ref('construction_management_app.action_sub_contract_agreement_report').report_action(self)