from odoo import api, models, fields


class ProforomaInvoice(models.Model):
    _name = 'proforma.invoice'

    name = fields.Char(string="Name")
    sale_order_id = fields.Many2one('sale.order')
    sale_name = fields.Char(string="Sale")
    sale_order_value = fields.Float(string="Sale Order Value")
    description = fields.Text(string="Description")
    project_id = fields.Many2one('project.project', string="Project")
    task_ids = fields.Many2many('project.task', string="Completed Phases")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    partner_id = fields.Many2one('res.partner')
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    amount = fields.Selection([('percent', 'By Percentage'), ('fixed', 'BY Fixed Amount')], string="Amount")
    percentage = fields.Float(string="Percentage")
    fixed_amount = fields.Float(string="Fixed Amount")
    final_amount = fields.Float(string="Final Amount", compute='compute_final_amount', store=True)
    remaining_amount = fields.Float(string="Remaining Amount", compute='compute_final_amount', store=True)
    tax_amount = fields.Float(string="Tax Amount", compute='compute_tax_amount', store=True)
    tax_excluded = fields.Float(string="Tax Excluded", compute='compute_tax_amount', store=True)
    tax_included = fields.Float(string="Tax Included", compute='compute_tax_amount', store=True)



    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('proforma.invoice') + '/'+ vals.get('sale_name')
        vals.update({
            'name': name
        })
        result = super(ProforomaInvoice, self).create(vals)
        if result['project_id']:
            projects = self.env['project.project'].search([('id', '=', result['project_id'].id)])
            tasks = projects.project_task_ids.filtered(lambda l: l.id in result['task_ids'].ids)
            for task in tasks:
                task.proforma_generated = 'yes'
        return result

    def print_proforma_invoice(self):
        return self.env.ref('construction_management_app.action_proforma_invoice_report').report_action(self)

    @api.depends('percentage', 'fixed_amount')
    def compute_final_amount(self):
        for rec in self:
            if rec.percentage:
                percent = rec.sale_order_value * (rec.percentage/100)
                rec.final_amount = percent
                rec.remaining_amount = rec.sale_order_value - percent
            if rec.fixed_amount:
                rec.final_amount = rec.fixed_amount
                rec.remaining_amount = rec.sale_order_value - rec.fixed_amount
                
    @api.depends('tax_ids')
    def compute_tax_amount(self):
        for rec in self:
            taxes = rec.tax_ids.compute_all(rec.final_amount, rec.company_id.currency_id, partner=rec.partner_id)
            rec.tax_amount = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            rec.tax_included = taxes['total_included']
            rec.tax_excluded = taxes['total_excluded']

                

        
