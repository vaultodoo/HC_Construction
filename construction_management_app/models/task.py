# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MaterialPlanning(models.Model):
    _name = 'material.plan'
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.description = self.product_id.name

    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )

    total_qty = fields.Float(string="Qty Onhand")
    qty_to_purchase = fields.Float(string="Qty to Purchase")

    description = fields.Char(
        string='Description'
    )
    product_uom_qty = fields.Integer(
        'Quantity',
    )
    product_uom = fields.Many2one(
        'uom.uom',
        'Unit of Measure'
    )
    material_task_id = fields.Many2one(
        'project.task',
        'Material Plan Task'
    )
    material_project_id = fields.Many2one('project.project', 'Project')
    project_id = fields.Many2one('project.project', 'Project')

    @api.onchange('product_id')
    def compute_qty_on_hand(self):
        for rec in self:
            if rec.product_id:
                rec.total_qty = rec.product_id.qty_available

    @api.onchange('product_uom_qty')
    def compute_qty_to_purchase(self):
        if self.product_uom_qty > self.total_qty:
            self.qty_to_purchase = self.product_uom_qty - self.total_qty


class LabourPlanning(models.Model):
    _name = 'labour.plan'

    labour_no = fields.Integer(string="No.of Labours")
    no_days = fields.Float(string="No. of Days")
    task_id = fields.Many2one('project.task')
    project_id = fields.Many2one('project.project')
    planned_hours = fields.Float(string="Planned Hours", compute='compute_planned_hours', store=True)
    working_hours = fields.Float(string="Working Hours")

    @api.depends('labour_no', 'no_days', 'working_hours')
    def compute_planned_hours(self):
        for rec in self:
            rec.planned_hours = rec.labour_no * rec.no_days * rec.working_hours
            if rec.task_id:
                rec.task_id.planned_hours = rec.planned_hours


class ConsumedMaterial(models.Model):
    _name = 'consumed.material'
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.description = self.product_id.name

    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )
    description = fields.Char(
        string='Description'
    )
    product_uom_qty = fields.Integer(
        'Quantity',
        default=1.0
    )
    product_uom = fields.Many2one(
        'uom.uom',
        'Unit of Measure'
    )
    consumed_task_material_id = fields.Many2one(
        'project.task',
        'Consumed Material Plan Task'
    )


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _order = "priority desc, sequence, id asc"

    
    # @api.multi #odoo13
    # @api.depends('picking_ids.move_lines')
    # def _compute_stock_picking_moves(self):
    #     for rec in self:
    #         rec.ensure_one()
    #         for picking in rec.picking_ids:
    #             rec.move_ids = picking.move_lines.ids

    @api.depends()
    def _compute_stock_picking_moves(self):
        move_ids = self.env['stock.move']
        for rec in self:
            for requisition in rec.picking_ids:
                picking_ids = self.env['stock.picking'].search([('custom_requisition_id','=',requisition.id)])
                for picking in picking_ids:
                    for move in picking.move_ids_without_package:
                        move_ids += move
            rec.move_ids = [(6,0, move_ids.ids)]

    def total_stock_moves_count(self):
        for task in self:
            task.stock_moves_count = len(task.move_ids)
    
    def _compute_notes_count(self):
        for task in self:
            task.notes_count = len(task.notes_ids)

    picking_ids = fields.One2many(
        'material.purchase.requisition',
        'custom_task_id',
        'Stock Pickings'
    )
    
    # picking_ids = fields.One2many(
    #     'stock.picking',
    #     'task_id',
    #     'Stock Pickings'
    # )
    move_ids = fields.Many2many(
        'stock.move',
        compute='_compute_stock_picking_moves',
    )
    return_mov_ids = fields.Many2many('stock.move', 'returned_stock_move_rel', 'task_id', 'move_id', string="Return Moves")

    # move_ids = fields.Many2many(
    #     'stock.move',
    #     compute='_compute_stock_picking_moves',
    #     store=True,
    # )
    material_plan_ids = fields.One2many(
        'material.plan',
        'material_task_id',
        'Material Plannings'
    )
    consumed_material_ids = fields.One2many(
        'consumed.material',
        'consumed_task_material_id',
        'Consumed Materials'
    )
    # stock_moves_count = fields.Integer(
    #     compute='total_stock_moves_count', 
    #     string='# of Stock Moves',
    #     store=True,
    # )
    stock_moves_count = fields.Integer(
        compute='total_stock_moves_count', 
        string='# of Stock Moves',
        store=True,
    )
    parent_task_id = fields.Many2one(
        'project.task', 
        string='Parent Task', 
        readonly=True
    )
    child_task_ids = fields.One2many(
        'project.task', 
        'parent_task_id', 
        string='Child Tasks'
    )
    notes_ids = fields.One2many(
        'note.note', 
        'task_id', 
        string='Notes',
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count', 
        string="Notes"
    )
    start_date = fields.Datetime(string="Start Date")
    stage = fields.Char(string='Stage', related="stage_id.name", store=True)
    final_stage = fields.Boolean(related="stage_id.final_stage", store=True)
    phase_id = fields.Many2one('project.phase.template', string="Project Phase")
    proforma_generated = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Proforma Generated', default='no')
    # @api.multi #odoo13
    def view_stock_moves(self):
        for rec in self:
            stock_move_list = []
            for move in rec.move_ids:
                stock_move_list.append(move.id)
        # result = self.env.ref('stock.stock_move_action')
        result = self.env.ref('stock.stock_move_action')
        action_ref = result or False
        result = action_ref.read()[0]
        result['domain'] = str([('id', 'in', stock_move_list)])
        return result
        
    # @api.multi #odoo13
    def view_notes(self):
        for rec in self:
            res = self.env.ref('construction_management_app.action_task_note_note')
            res = res.read()[0]
            res['domain'] = str([('task_id', 'in', rec.ids)])
        return res

    def return_all_moves(self):
        moves = []
        if self.move_ids:
            for rec in self.move_ids:
                if not rec.is_returned:
                    for line in rec.move_line_nosuggest_ids:
                        pro_line = self.env['return.moves.products'].create({
                            'product_id': line.product_id.id,
                            'lot_id': line.lot_id.id,
                            'total_qty': line.qty_done,
                            'product_uom': line.product_uom_id.id,
                            'task_id': self.id,
                            'move_id': rec.id,
                        })
                        moves.append(pro_line.id)
        return {
            'name': _('Return Product'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'return.stock.move',
            'target': 'new',
            'context': {'default_return_product_ids': moves, 'default_move_ids': self.move_ids.ids, 'default_task_id': self.id}
        }

    def compute_consumed_materials(self):
        if self.move_ids or self.return_mov_ids:
            for moves in self.move_ids:
                if moves.product_id.id in self.return_mov_ids.mapped('product_id').ids and moves.product_id.id not in self.consumed_material_ids.mapped('product_id').ids:
                    r_moves = self.return_mov_ids.filtered(lambda l : l.product_id.id == moves.product_id.id)
                    qty = moves.product_uom_qty - r_moves.product_uom_qty
                    self.consumed_material_ids = [(0, 0, {'product_id': moves.product_id.id,
                                                          'product_uom_qty': qty,
                                                          'product_uom': moves.product_uom.id,
                                                                   })]
                else:
                    if moves.product_id.id not in self.consumed_material_ids.mapped('product_id').ids:
                        self.consumed_material_ids = [(0, 0, {'product_id': moves.product_id.id,
                                                                'product_uom_qty': moves.product_uom_qty,
                                                                'product_uom': moves.product_uom.id,
                                                                })]

class StockMove(models.Model):
    _inherit = 'stock.move'

    is_returned = fields.Boolean(string="Is Returned?")
    returned_reason = fields.Text(string="Returned Reason")

    def return_product(self):
        for rec in self:
            moves = []
            for line in rec.move_line_nosuggest_ids:
                pro_line = self.env['return.moves.products'].create({
                    'product_id': line.product_id.id,
                    'lot_id': line.lot_id.id,
                    'total_qty': line.qty_done,
                    'product_uom':line.product_uom_id.id,
                    'move_id': self.id,
                    'task_id': rec.picking_id.custom_requisition_id.custom_task_id.id
                })
                moves.append(pro_line.id)
        task = self[0].picking_id.custom_requisition_id.custom_task_id.id if self else False
        return {
            'name': _('Return Product'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'return.stock.move',
            'target': 'new',
            'context': {'default_return_product_ids':  moves, 'default_move_ids': self.ids, 'default_task_id': task}
        }


class ReturnMove(models.TransientModel):
    _name = 'return.stock.move'

    move_ids = fields.Many2many('stock.move')
    task_id = fields.Many2one('project.task')
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True,
        copy=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        copy=True,
    )

    return_date = fields.Date(
        string='Return Date',
        copy=False,
    )
    reason = fields.Text(
        string='Reason for Return',
        required=False,
        copy=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=False,
        copy=True,
    )
    delivery_picking_id = fields.Many2one(
        'stock.picking',
        string='Internal Picking',
        readonly=True,
        copy=False,
    )
    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False,
    )
    return_product_ids = fields.Many2many('return.moves.products', string="Return Products")

    def return_products(self):
        if self.return_product_ids:
            for rec in self.return_product_ids:
                new_move = self.env['stock.move'].create({
                    'name': _('New Move:') + rec.product_id.display_name,
                    'product_id': rec.product_id.id,
                    'product_uom_qty': rec.return_qty,
                    'product_uom': rec.product_uom.id,
                    # 'description_picking': ops.description_picking,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.dest_location_id.id,
                    'origin': _('Return Of ') + rec.move_id.picking_id.origin,
                    'picking_type_id': self.custom_picking_type_id.id,
                    'restrict_partner_id': self.employee_id.user_id.partner_id.id,
                    'company_id': self.employee_id.user_id.company_id.id,
                    'is_returned': True,
                    'returned_reason': self.reason

                })
                move_lines = self.env['stock.move.line'].create({
                    'date': self.return_date,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.dest_location_id.id,
                    'lot_id': rec.lot_id.id,
                    'move_id': new_move.id,
                    'product_id': rec.product_id.id,
                    'qty_done': rec.return_qty,
                    'product_uom_id': rec.product_uom.id,
                    'state': 'done'
                })

                new_move.update({
                    'move_line_nosuggest_ids': move_lines.ids,
                    'move_line_ids': move_lines.ids
                })
                move = new_move._action_confirm()
                move._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
                rec.move_id.is_returned = True
                rec.move_id.returned_reason = self.reason
                rec.task_id.return_mov_ids = [(4, move.id)]


class ReturnMovesProducts(models.Model):
    _name = 'return.moves.products'

    product_id = fields.Many2one('product.product', string="Product")
    lot_id = fields.Many2one('stock.production.lot', string="Lot/Serial No")
    total_qty = fields.Float(string="Total Qty")
    return_qty = fields.Float(string="Return Qty")
    product_uom = fields.Many2one('uom.uom')
    move_id = fields.Many2one('stock.move')
    task_id = fields.Many2one('project.task')

    @api.onchange('return_qty')
    def quantity_return_warning(self):
        if self.return_qty > self.total_qty:
            raise ValidationError("Return quantity cannot be greater than total quantity")


