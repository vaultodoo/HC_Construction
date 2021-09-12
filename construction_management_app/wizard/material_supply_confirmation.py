from odoo import api, models, fields
import base64


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
        self.get_report_attachment()
        return self.env.ref('construction_management_app.action_material_supply_confirmation_report').report_action(self)

    def get_report_attachment(self):
        REPORT_ID = 'construction_management_app.action_material_supply_confirmation_report'
        pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.id)
        b64_pdf = base64.b64encode(pdf[0])
        ATTACHMENT_NAME = 'Material Supply Confirmation'
        self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'res_model': 'project.project',
            'res_id': self.project_id.id,
            'mimetype': 'application/x-pdf'
        })
