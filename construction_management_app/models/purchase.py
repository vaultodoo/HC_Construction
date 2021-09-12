# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    other_reference = fields.Char(string="Other Reference")
    dispatch_through = fields.Char(string="Dispatch Through")
    destination = fields.Char(string="Destination")
    delivery_terms = fields.Char(string="Terms of Delivery")
    amount_text = fields.Char(compute='get_amount_to_text', store=True)

    @api.depends('amount_total')
    def get_amount_to_text(self):
        for rec in self:
            rec.amount_text = rec.company_id.currency_id.amount_to_text(rec.amount_total)

#     picking_id = fields.Many2one(
#         'stock.picking',
#         string='Stock Picking',
#     )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

