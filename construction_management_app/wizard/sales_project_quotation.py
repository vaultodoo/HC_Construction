from odoo import api, models, fields
import base64

class SalesProjectQuotation(models.TransientModel):
    _name = 'sales.project.quotation'

    date = fields.Date(default=fields.Date.context_today)
    attention = fields.Text(string="Attention")
    subject = fields.Text(string="Subject")
    scope_work = fields.Text(string="Scope of Work")
    wet_area = fields.Text(string="Wet Area")
    guarantee = fields.Text(string="Guarantee")
    commencement = fields.Text(string="Commencement")
    contract = fields.Text(string="Contract")
    nature_work = fields.Html(string="Nature of work")
    exclusions = fields.Html()
    special_notes = fields.Html()
    project_id = fields.Many2one('project.project', default=lambda self: self.env['project.project'].search([('sale_order_id', '=', self._context.get('active_id', False))], limit=1))
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    sale_id = fields.Many2one('sale.order', default=lambda self: self._context.get('active_id', False))

    def print_report(self):
        self.get_report_attachment()
        return self.env.ref('construction_management_app.action_sales_project_quotation_report').report_action(self)

    def get_report_attachment(self):
        REPORT_ID = 'construction_management_app.action_sales_project_quotation_report'
        pdf = self.env.ref(REPORT_ID).render_qweb_pdf(self.id)
        b64_pdf = base64.b64encode(pdf[0])
        ATTACHMENT_NAME = 'Project Quotation Report'
        self.env['ir.attachment'].create({
            'name': ATTACHMENT_NAME,
            'type': 'binary',
            'datas': b64_pdf,
            'res_model': 'sale.order',
            'res_id': self.sale_id.id,
            'mimetype': 'application/x-pdf'
        })


