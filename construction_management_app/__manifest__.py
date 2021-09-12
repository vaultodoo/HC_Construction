# -*- coding: utf-8 -*-

# Part of Vault Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Construction Management',
    'version': '18.8',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'author': 'Vault Odoo',
    'support': 'vaultodoo@gmail.com',
    'images': ['static/description/img1.jpg'],
    'category': 'Project',
    'summary':  """This module provide Construction Management Related Activity.""",
    'description': """
This module provide Construction Management Related Activity.
Construction
Construction Projects
Budgets
Notes
Materials
Material Request For Job Orders
Add Materials
Job Orders
Create Job Orders
Job Order Related Notes
Issues Related Project
Vendors
Vendors / Contractors

Construction Management
Construction Activity
Construction Jobs
Job Order Construction
Job Orders Issues
Job Order Notes
Construction Notes
Job Order Reports
Construction Reports
Job Order Note
Construction app
Construction 
job costing
job cost sheet
job contracting
Construction Management

This module provide feature to manage Construction Management activity.
Menus:
Construction
Construction/Configuration
Construction/Configuration /Stages
Construction/Construction
Construction/Construction/Budgets
Construction/Construction/Notes
Construction/Construction/Projects
Construction/Job Orders
Construction/Job Orders /Issues
Construction/Job Orders /Job Orders
Construction/Job Orders /Notes
Construction/Materials / BOQ
Construction/Materials /Material Requisitions / BOQ
Construction/Materials /Materials
Construction/Vendors
Construction/Vendors /Contractors
Defined Reports
Notes
Project Report
Task Report
Construction Project - Project Manager
real estate property
propery management
bill of material
Material Planning On Job Order

Bill of Quantity On Job Order
Bill of Quantity construction
    """,
    'depends': ['project', 
                'stock',
                'stock_account',
                # 'odoo_account_budget',
                'purchase',
#                'project_issue',
                'hr_timesheet',
                'note',
                'material_purchase_requisitions',
                'project_task_material_requisition',
                'sale_timesheet',
                'sale'
                ],
    'data': [
             'security/construction_security.xml',
             'security/ir.model.access.csv',
             'wizard/project_user_subtask_view.xml',
             'views/construction_management_view.xml',
             # 'wizard/purchase_order_view.xml',
             'views/project_task_view.xml',
             'views/project_view.xml',
             'views/note_view.xml',
             'views/report_noteview.xml',
             'views/report_reg.xml',
             'views/project_report.xml',
             'views/project_task_view.xml',
             'views/task_report.xml',
             'views/purchase_view.xml',
            # 'views/stock_picking.xml',
             'views/product_view.xml',
             'views/purchase_requisition_view.xml',
             'views/project_phase_template.xml',
            'views/proforma_invoice.xml',
            'reports/sale_profoma_report.xml',
        'reports/customer_survey_form.xml',
        'views/proforma_email_template.xml',
        'reports/water_proofing_completion_report.xml',
        'wizard/water_proofing_completion.xml',
        'reports/sub_contract_agreement_report.xml',
        'wizard/sub_contract_agreement.xml',
        'reports/water_proofing_guarantee_report.xml',
        'wizard/water_proofing_guarantee.xml',
        'reports/invoice_report_inherit.xml',
        'reports/material_supply_confirmation_report.xml',
        'wizard/material_supply_confirmation.xml',
        'reports/purchase_order_report.xml',
        # 'reports/sales_project_quotation_report.xml',
        # 'wizard/sales_project_quotation.xml',
        'data/sequence.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
