from odoo import api, models, fields
import base64


class SaleSubContractAgreement(models.TransientModel):
    _name = 'sale.sub.contract.agreement'

    date = fields.Date(default=fields.Date.context_today)
    client = fields.Text(string="Client/Owner")
    consultant = fields.Text(string="Consultant")
    contact = fields.Text(string="Contact")
    nature_work = fields.Html(string="Nature of work")
    guarantee = fields.Text(string="Guarantee")
    commencement = fields.Text(string="Commencement")
    contract = fields.Text(string="Contract")
    sale_id = fields.Many2one('sale.order', default=lambda self: self._context.get('active_id', False))
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def print_report(self):
        self.get_report_attachment()
        return self.env.ref('construction_management_app.action_sale_sub_contract_agreement_report').report_action(self)

    def get_report_attachment(self):
        REPORT_ID = 'construction_management_app.action_sale_sub_contract_agreement_report'
        pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.id)
        b64_pdf = base64.b64encode(pdf[0])
        ATTACHMENT_NAME = 'Sub Contract Agreement'
        self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'res_model': 'sale.order',
            'res_id': self.sale_id.id,
            'mimetype': 'application/x-pdf'
        })
