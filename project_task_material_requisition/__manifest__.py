# -*- coding: utf-8 -*-

# Part of Vault Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Material Requisition for Project and Task Integration",
    'version': '1.1.5',
    'category' : 'Project/Project',
    'price': 29.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This app allow you to select Project and Task on Material Purchase Requisition.""",
    'author': "Vault Odoo",
    'support': 'vaultodoo@gmail.com',
    'images': ['static/description/mrimg1.jpg'],
    'description': """
This app allow you to set Project and Task on Material Purchase Requisition.
Project Material Requisition Smart Button
Task Material Purchase Requisition
Material Purchase Requisition Group By Project
Material Purchase Requisition Group By Task
Material Purchase Requisition
Material requisition
    """,
    'depends': [
                'project',
                'material_purchase_requisitions',
                ],
    'data':[
       'views/material_purchase_requisition_view.xml',
       'views/project_view.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
