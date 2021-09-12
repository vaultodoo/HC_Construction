from odoo import api, models, fields


class SalesProjectQuotation(models.TransientModel):
    _name = 'sales.project.quotation'

    date = fields.Date(default=fields.Date.context_today)
    attention = fields.Text(string="Attention")
    subject = fields.Text(string="Subject")
    scope_work = fields.Text(string="Scope of Work")
    special_note = fields.Text(string="Wet Area,Exclusions,Special Notes")
    guarantee = fields.Text(string="Guarantee")
    commencement = fields.Text(string="Commencement")
    contract = fields.Text(string="Contract")
    nature_work = fields.Html(string="Nature of work")
    project_id = fields.Many2one('project.project', default=lambda self: self.env['project.project'].search([('sale_order_id', '=', self._context.get('active_id', False))], limit=1))
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    sale_id = fields.Many2one('sale.order', default=lambda self: self._context.get('active_id', False))

    def print_report(self):
        return self.env.ref('construction_management_app.action_sales_project_quotation_report').report_action(self)

