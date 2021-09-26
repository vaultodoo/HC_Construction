# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'mail.activity.mixin']

    type_of_construction = fields.Selection(
        [('agricultural', 'Agricultural'),
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('institutional','Institutional'),
        ('industrial','Industrial'),
        ('heavy_civil', 'Heavy civil'),
        ('environmental', 'Environmental'),
        ('other', 'other')],
        string='Types of Construction',  track_visibility='onchange'
    )
    construction_type = fields.Many2one(
        'construction.type',
        string='Project Type', track_visibility='onchange'
    )
    location_id = fields.Many2one(
        'res.partner',
        'Location',tracking=True
    )
    location = fields.Char(string="Location", tracking=True)
    notes_ids = fields.One2many(
        'note.note', 
        'project_id', 
        string='Notes', tracking=True
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count', 
        string="Notes",
        store=True,tracking=True
    )
    source_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        copy=True,tracking=True
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=False,
        copy=True,tracking=True
    )
    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False,tracking=True
    )

    project_phase_ids = fields.Many2many('project.phase.template', string="Project Phases",tracking=True)
    stage_allocated = fields.Boolean(tracking=True)
    sales_person = fields.Many2one('res.users', string="User",tracking=True)
    s_person = fields.Many2one('hr.employee', string="Sales Person", tracking=True)
    project_manager = fields.Many2one('hr.employee', string="Project Manager", tracking=True)
    user_id = fields.Many2one('res.users',string='Project User',default=lambda self: self.env.user,tracking=True)
    job_order = fields.Char(string="Job Order",tracking=True)
    plot_no = fields.Char(string="Plot No",tracking=True)
    document_ids = fields.One2many('upload.documents', 'project_id', string="Documents",tracking=True)
    stage_id = fields.Many2one('project.phase.template', ondelete='restrict', tracking=True, index=True, copy=False, domain="[('id', 'in', project_phase_ids)]")
    project_task_ids = fields.One2many('project.task', 'project_id',tracking=True)
    project_material_plan_ids = fields.One2many(
        'material.plan',
        'material_project_id',
        'Material Plannings',tracking=True
    )
    project_labour_plan_ids = fields.One2many('labour.plan', 'project_id', 'Labour Plannings',tracking=True)
    contract_date = fields.Date(string="PO/Contract Date",tracking=True)
    invoice_count = fields.Integer(compute='compute_proforma_count')
    proforma_count = fields.Integer(compute='compute_proforma_count')
    proforma_paid = fields.Integer(compute='compute_proforma_count')
    proforma_pending = fields.Integer(compute='compute_proforma_count')
    total_sale_cost = fields.Float(compute='get_project_value')
    untaxed_sale_cost = fields.Float(compute='get_project_value')
    total_material_cost = fields.Float(compute='get_project_value')
    planned_material_cost = fields.Float(compute='get_project_value')
    planned_labour_cost = fields.Float(compute='get_project_value')
    other_expenses = fields.Float(compute='get_project_value')
    profit_amount = fields.Float(compute='get_project_value')
    profit_percent = fields.Float(compute='get_project_value')
    total_labour_cost = fields.Float(compute='get_project_value')
    other_expenses_ids = fields.One2many('other.expense', 'expense_id')
    final_profit_amount = fields.Float(compute='get_project_value')
    paid_invoice_amount = fields.Float(compute='get_invoice_amount')
    pending_invoice_amount = fields.Float(compute='get_invoice_amount')
    project_start_date = fields.Date()
    project_end_date = fields.Date()
    working_days = fields.Char(string="No. of working days")

    def get_invoice_amount(self):
        for rec in self:
            paid = 0.0
            pending = 0.0
            if rec.sale_order_id:
                paid = sum(self.env['account.move'].search([('sale_order_id', '=', rec.sale_order_id.id)]).mapped('amount_total'))-sum(self.env['account.move'].search([('sale_order_id', '=', rec.sale_order_id.id)]).mapped('amount_residual'))
                pending= sum(self.env['account.move'].search([('sale_order_id', '=', rec.sale_order_id.id)]).mapped('amount_residual'))
            rec.paid_invoice_amount = paid
            rec.pending_invoice_amount = pending

    def get_project_value(self):
        for rec in self:
            rec.total_sale_cost = rec.sale_order_id.amount_total if rec.sale_order_id else 0.0
            rec.untaxed_sale_cost = rec.sale_order_id.amount_untaxed if rec.sale_order_id else 0.0
            if rec.project_task_ids:
                material = 0.0
                employee_cost = 0.0
                for task in rec.project_task_ids:
                    price = sum(task.consumed_material_ids.mapped('total_price'))
                    emp_cost = sum(task.timesheet_ids.mapped('total_price'))
                    material += price
                    employee_cost += emp_cost
                rec.total_material_cost = material
                rec.total_labour_cost = employee_cost
            total_cost = rec.total_labour_cost + rec.total_material_cost
            rec.profit_amount = rec.untaxed_sale_cost - total_cost
            rec.profit_percent = (rec.profit_amount/rec.untaxed_sale_cost)*100 if rec.untaxed_sale_cost else 0.0
            rec.planned_labour_cost = sum(rec.project_labour_plan_ids.mapped('total_cost'))
            rec.planned_material_cost = sum(rec.project_material_plan_ids.mapped('total_cost'))
            rec.other_expenses = sum(rec.other_expenses_ids.mapped('cost'))
            expense = 0.0
            if rec.other_expenses_ids:
                expense = sum(rec.other_expenses_ids.mapped('cost'))
            rec.final_profit_amount = rec.profit_amount - expense

    @api.onchange('job_order')
    def job_order_warning(self):
        exists = self.env['project.project'].search([('job_order','=',self.job_order)])
        if exists:
            raise ValidationError("You cannot create multiple projects with same job order")

    @api.onchange('contract_date', 'job_order', 's_person', 'project_manager')
    def get_sale_order_details(self):
        if self.sale_order_id:
            self.sale_order_id.contract_date = self.contract_date
            self.sale_order_id.job_order = self.job_order
            self.sale_order_id.sales_person = self.s_person.id
            self.sale_order_id.project_manage = self.project_manager.id

    @api.depends()
    def _compute_notes_count(self):
        for project in self:
            project.notes_count = len(project.notes_ids)

    # @api.multi #odoo13
    def view_notes(self):
        for rec in self:
            res = self.env.ref('construction_management_app.action_project_note_note')
            res = res.read()[0]
            res['domain'] = str([('project_id', 'in', rec.ids)])
        return res

    @api.model
    def create(self,vals):
        rtn = super(ProjectProject,self).create(vals)
        location_settings = self.env['location.settings'].search([],limit=1)
        rtn.source_location_id = location_settings.location_id.id
        rtn.dest_location_id = location_settings.dest_location_id.id
        rtn.custom_picking_type_id = location_settings.custom_picking_type_id.id
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
        if not completed_phases:
            raise ValidationError("There is No completed phase for invoicing")
        else:
            return {
                "name": _("Pro-Forma Invoice"),
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "proforma.invoice",
                "target": "new",
                'context': {'default_sale_order_id': self.sale_order_id.id, 'default_project_id': self.id,
                            'default_sale_order_value': self.sale_order_id.amount_total, 'default_task_ids': completed_phases.ids,
                            'default_sale_name': self.sale_order_id.name, 'default_partner_id': self.partner_id.id,
                            'default_amount_untaxed': self.sale_order_id.amount_untaxed, 'default_amount_tax': self.sale_order_id.amount_tax}
            }

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": self.sale_order_id.id,
            "context": {"create": False, "show_sale": True},
        }
    
    def compute_proforma_count(self):
        for rec in self:
            rec.proforma_count = self.env['proforma.invoice'].search_count([('project_id', '=', rec.id)])
            rec.proforma_pending = self.env['proforma.invoice'].search_count([('project_id', '=', rec.id), ('state', '=', 'new')])
            rec.proforma_paid = self.env['proforma.invoice'].search_count([('project_id', '=', rec.id), ('state', '=', 'paid')])
            rec.invoice_count = self.env['account.move'].search_count([('sale_order_id', '=', rec.sale_order_id.id)])

    def action_view_proforma(self):
        proformas = self.env['proforma.invoice'].search([('project_id', '=', self.id)]).ids

        return {
            'type': 'ir.actions.act_window',
            'name': 'Proforma Invoices',
            'view_mode': 'tree,form',
            'res_model': 'proforma.invoice',
            'domain': [('id', 'in', proformas)],
        }
    
    def action_open_sale_invoices(self):
        if self.sale_order_id:
            invoices = self.env['account.move'].search([('sale_order_id', '=', self.sale_order_id.id)]).ids
            return {
                'type': 'ir.actions.act_window',
                'name': 'Account Invoices',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'domain': [('id', 'in', invoices)],
            }

    def generate_transfer(self):
        if self.project_material_plan_ids:
            transfer_lines = self.project_material_plan_ids.filtered(lambda l: l.transfer_generated != 'yes').mapped('material_task_id')
            for task in transfer_lines:
                transfers = self.project_material_plan_ids.filtered(lambda l: l.transfer_generated != 'yes' and l.material_task_id.id == task.id)
                values = {
                    'custom_project_id': self.id,
                    'custom_task_id': task.id,
                    'requisition_line_ids': [(0, 0, {
                        'requisition_type': 'internal',
                        'product_id': t.product_id.id,
                        'description': t.description,
                        'qty': t.product_uom_qty,
                        'uom': t.product_uom.id
                    }) for t in transfers],
                    'location_id': self.source_location_id.id,
                    'dest_location_id': self.dest_location_id.id,
                    'custom_picking_type_id': self.custom_picking_type_id.id

                }

                requisition = self.env['material.purchase.requisition'].create(values)
                requisition.request_stock()
                pickings = self.env['stock.picking'].search([('custom_requisition_id','=',requisition.id),('state','=','draft')])
                pickings.action_confirm()
                pickings.action_assign()
                pickings.sudo().button_validate()
                if pickings:

                    pick_to_backorder = self.env['stock.picking']
                    pick_to_do = self.env['stock.picking']
                    for picking in pickings:
                        # If still in draft => confirm and assign
                        if picking.state == 'draft':
                            picking.action_confirm()
                            if picking.state != 'assigned':
                                picking.action_assign()
                                if picking.state != 'assigned':
                                    raise UserError(
                                        _("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
                        for move in picking.move_lines.filtered(lambda m: m.state not in ['done','cancel']):
                            for move_line in move.move_line_ids:
                                move_line.qty_done = move_line.product_uom_qty
                        if picking._check_backorder():
                            pick_to_backorder |= picking
                            continue
                        pick_to_do |= picking
                    # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
                    if pick_to_do:
                        pick_to_do.action_done()
                    for tt in transfers:
                        tt.transfer_generated = 'yes'
                    if pick_to_backorder:
                        return pick_to_backorder.action_generate_backorder_wizard()


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
            self.phase_ids = [(4, i)for i in self.project_id.project_phase_ids.ids]


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    project_name = fields.Char(string="Project Name")
    job_order = fields.Char(string="Job Order")
    contract_date = fields.Date(string="PO/Contract Date")
    project_manager = fields.Many2one('res.users', string="Project User")
    project_manage = fields.Many2one('hr.employee', string="Project Manager")

    sales_person = fields.Many2one('hr.employee', string="Sales Person", tracking=True)
    sales_target = fields.Float(related='sales_person.sales_target', store=True)
    validity = fields.Char(string="Validity")
    user_id = fields.Many2one(
        'res.users',string='User',index=True,tracking=2,default=lambda self: self.env.user,
        domain=lambda self: [('groups_id','in',self.env.ref('sales_team.group_sale_salesman').id)])

    @api.onchange('contract_date', 'job_order', 'project_manage', 'sales_person')
    def onchange_sale_order_details(self):
        if self.project_ids:
            for pro in self.project_ids:
                pro.contract_date = self.contract_date
                pro.job_order = self.job_order
                pro.s_person = self.sales_person.id
                pro.project_manager = self.project_manage.id

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self,fields.Datetime.to_datetime(vals['date_order']))
            initial = self.env['hr.employee'].search([('id', '=', vals.get('sales_person'))]).employee_initial
            split_seq = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                'sale.order.seq',sequence_date=seq_date).split('/')[2]
            initial_split_concat = initial + "-" + split_seq if initial else split_seq
            split = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                'sale.order.seq', sequence_date=seq_date)[0:-5]
            seq = split + initial_split_concat + "/" + str(fields.Date.today().year)
            vals['name'] = seq or _('New')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id','partner_shipping_id','pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery','invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id',addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id',addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id',
                                                   partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(SaleOrder, self).create(vals)
        return result

    def action_open_sale_project(self):
        action = {
            'type': 'ir.actions.act_window',
            'views': [(False, 'form')],
            'view_mode': 'form',
            'name': _('Projects'),
            'res_model': 'project.project',
            "res_id": self.project_ids.id,
            "context": {"create": False,"show_sale": True},
        }
        return action

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        # ensure a correct context for the _get_default_journal method and company-dependent fields
        self = self.with_context(default_company_id=self.company_id.id, force_company=self.company_id.id)
        journal = self.env['account.move'].with_context(default_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'sales_person': self.sales_person.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'invoice_partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'journal_id': journal.id,  # company comes from the journal
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_payment_ref': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'sale_order_id':self.id
        }
        return invoice_vals



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_project_prepare_values(self):
        """Generate project values"""
        account = self.order_id.analytic_account_id
        if not account:
            self.order_id._create_analytic_account(prefix=self.product_id.default_code or None)
            account = self.order_id.analytic_account_id

        return {
            'name': '%s' % self.order_id.project_name if self.order_id.project_name else self.order_id.name,
            'analytic_account_id': account.id,
            'partner_id': self.order_id.partner_id.id,
            'sale_line_id': self.id,
            'sale_order_id': self.order_id.id,
            'active': True,
            'company_id': self.company_id.id,
            's_person': self.order_id.sales_person.id,
            'project_manager': self.order_id.project_manage.id
        }

class ConstructionType(models.Model):
    _name = 'construction.type'

    name = fields.Char(required=1)
    code = fields.Char(required=1)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_initial = fields.Char(string="Partner Initial")


class OtherExpense(models.Model):
    _name = 'other.expense'

    expense = fields.Char(string="Expense")
    cost = fields.Float(string="Cost")
    expense_id = fields.Many2one('project.project')

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    price_unit = fields.Float(compute='get_employee_rate', store=True)
    total_price = fields.Float(compute='get_employee_rate', store=True)

    @api.depends('employee_id')
    def get_employee_rate(self):
        for rec in self:
            if rec.employee_id:
                rec.price_unit = rec.employee_id.timesheet_cost
                rec.total_price = rec.price_unit * rec.unit_amount


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order')

    sales_person = fields.Many2one('hr.employee', string="Sales Person")

    invoice_user_id = fields.Many2one('res.users', copy=False,tracking=True,
                                      string='User',
                                      default=lambda self: self.env.user)
    monthly_target = fields.Float(string="Monthly Target", related='sales_person.monthly_target', store=True)

    amount_paid = fields.Float(compute='get_amount_paid_total')
    paid_amount = fields.Float(compute='get_paid_amount', store=True)

    def get_amount_paid_total(self):
        for rec in self:
            rec.amount_paid = rec.amount_total - rec.amount_residual

    @api.depends('amount_paid')
    def get_paid_amount(self):
        for rec in self:
            rec.paid_amount = rec.amount_paid


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = {
            'ref': order.client_order_ref,
            'type': 'out_invoice',
            'sale_order_id': order.id,
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'invoice_payment_ref': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'invoice_partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'sales_person': order.sales_person.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }

        return invoice_vals


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    invoice_user_id = fields.Many2one('res.users', string='User',readonly=True)
    sales_person = fields.Many2one('hr.employee', string="Sales Person")
    monthly_target = fields.Float(string="Monthly Target", related='sales_person.monthly_target', store=True)
    paid_amount = fields.Float(string="Amount Paid")


    _depends = {
        'account.move': ['sales_person']}

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.sales_person as sales_person, move.monthly_target, move.paid_amount"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", move.sales_person, move.monthly_target, move.paid_amount"


class SalesReport(models.Model):
    _inherit = 'sale.report'

    user_id = fields.Many2one('res.users','User',readonly=True)
    sales_person = fields.Many2one('hr.employee',string="Sales Person")
    sales_target = fields.Float(related='sales_person.sales_target',store=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['sales_person'] = ", s.sales_person as sales_person"
        fields['sales_target'] = ', s.sales_target as sales_target'

        groupby += ', s.invoice_status'

        return super(SalesReport, self)._query(with_clause, fields, groupby, from_clause)



class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    monthly_target = fields.Float(string="Monthly Target")
    sales_target = fields.Float(string="Sales Target")
    employee_initial = fields.Char(string="Employee Initial")


